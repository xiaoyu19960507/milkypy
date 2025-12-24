import json
import os

# Template for the beginning of the file
HEADER = """import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Union

import httpx
import websockets
from websockets.exceptions import ConnectionClosed

from .message import Text

logger = logging.getLogger("milkypy")

class MilkyClient:
    def __init__(
        self,
        host: str,
        port: Optional[int] = 3010,
        token: Optional[str] = None,
        api_port: Optional[int] = None,
        event_port: Optional[int] = None,
    ):
        self.host = host
        self.port = port
        self.token = token

        _api_port = api_port or port
        _event_port = event_port or port

        if _api_port is None or _event_port is None:
            raise ValueError("Either port, or both api_port and event_port must be provided.")

        self.ws_url = f"ws://{host}:{_event_port}/event"
        self.http_url = f"http://{host}:{_api_port}/api"
        self._ws: Optional[Any] = None
        self._handlers: Dict[str, list[Callable]] = {}

    def on(self, event_type: str):
        def decorator(func: Callable):
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(func)
            return func
        return decorator

    async def connect(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        while True:
            try:
                async with websockets.connect(self.ws_url, additional_headers=headers) as websocket:
                    self._ws = websocket
                    async for message in websocket:
                        await self._handle_message(message)
            except ConnectionClosed:
                logger.warning("WebSocket connection closed, reconnecting...")
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                await asyncio.sleep(1)

    async def _handle_message(self, message: Union[str, bytes]):
        try:
            data = json.loads(message)
            event_type = data["event_type"]
            
            if event_type in self._handlers:
                # Milky 协议事件中 'data' 字段包含实际负载
                payload = data["data"]
                self_id = data.get("self_id")
                time = data.get("time")
                
                for handler in self._handlers[event_type]:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(self, payload, self_id, time)
                    else:
                        handler(self, payload, self_id, time)
        except (KeyError, json.JSONDecodeError):
            # 忽略非协议消息或格式错误
            pass
        except Exception as e:
            logger.error(f"Failed to handle message: {e}")

    async def call_api(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        # Milky protocol primarily uses HTTP for API calls
        return await self.call_api_http(action, params)

    async def call_api_http(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        # Milky API endpoint is /api/:api
        url = f"{self.http_url}/{action}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=params or {},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            if data["status"] == "failed" or data.get("retcode", 0) != 0:
                raise RuntimeError(f"API call failed (retcode {data.get('retcode')}): {data.get('message', 'Unknown error')}")
            return data["data"]

    async def run(self):
        \"\"\"运行客户端\"\"\"
        await self.connect()

    # Helper methods for common APIs"""

TYPE_MAPPING = {
    "string": "str",
    "integer": "int",
    "boolean": "bool",
    "array": "List",
    "object": "Dict[str, Any]",
}

def resolve_ref(schema, root):
    if "$ref" in schema:
        ref_path = schema["$ref"].split("/")
        current = root
        for part in ref_path[1:]:
            current = current[part]
        return current
    return schema

def get_python_type(schema, root, is_docstring=False):
    if is_docstring:
        if "$ref" in schema:
            return schema["$ref"].split("/")[-1]
        if "allOf" in schema and len(schema["allOf"]) == 1:
             sub = schema["allOf"][0]
             if "$ref" in sub:
                 return sub["$ref"].split("/")[-1]

    schema = resolve_ref(schema, root)
    type_name = schema.get("type")
    
    if type_name == "array":
        items = schema.get("items", {})
        item_type = get_python_type(items, root, is_docstring)
        return f"List[{item_type}]"
    
    if "oneOf" in schema:
         # Simplified handling for oneOf, just use Any or Union if possible
         # For now, let's stick to Any or str/dict
         return "Any"
         
    return TYPE_MAPPING.get(type_name, "Any")

def generate_method(path, path_item, root):
    if "post" not in path_item:
        return ""
    
    operation = path_item["post"]
    operation_id = operation.get("operationId")
    if not operation_id:
        # fallback to path name
        operation_id = path.split("/")[-1]
        
    summary = operation.get("summary", "")
    
    # Extract params
    req_body = operation.get("requestBody", {})
    content = req_body.get("content", {}).get("application/json", {})
    schema = content.get("schema", {})
    
    schema = resolve_ref(schema, root)
    
    props = schema.get("properties", {})
    required = schema.get("required", [])
    
    args_list = []
    call_args = []
    param_docs = []
    
    # Sort: required first, then optional
    sorted_props = []
    for prop_name in props:
        if prop_name in required:
            sorted_props.append(prop_name)
    for prop_name in props:
        if prop_name not in required:
            sorted_props.append(prop_name)
            
    for prop_name in sorted_props:
        prop_schema = resolve_ref(props[prop_name], root)
        py_type = get_python_type(prop_schema, root)
        description = prop_schema.get("description", "")
        
        # Add enum info to description
        if "enum" in prop_schema:
             enums = [f'"{e}"' if isinstance(e, str) else str(e) for e in prop_schema["enum"]]
             description += f" ({' | '.join(enums)})"
        
        # Special handling for message to allow str
        if prop_name == "message" and "List" in py_type:
            py_type = "Union[str, List[dict]]"
        
        if prop_name in required:
            args_list.append(f"{prop_name}: {py_type}")
        else:
            default_val = "None"
            
            # Check if schema has default
            if "default" in prop_schema:
                default_v = prop_schema["default"]
                if isinstance(default_v, str):
                    default_val = f'"{default_v}"'
                elif isinstance(default_v, bool):
                    default_val = str(default_v)
                else:
                    default_val = str(default_v)
            else:
                 # If no default is provided in schema, use None and Optional type
                 if "Optional" not in py_type and py_type != "Any":
                     py_type = f"Optional[{py_type}]"
                 default_val = "None"

            args_list.append(f"{prop_name}: {py_type} = {default_val}")
            
        call_args.append(prop_name)
        
        # Add to param docs
        if description:
            param_docs.append(f"{prop_name}: {description}")
        else:
            param_docs.append(f"{prop_name}")

    args_str = ", ".join(args_list)
    if args_str:
        args_str = ", " + args_str
        
    # Construct body
    body = []
    body.append(f"    async def {operation_id}(self{args_str}) -> Dict[str, Any]:")
    
    # Generate Docstring
    docstring_lines = []
    if summary:
        docstring_lines.append(summary)
        
    if param_docs:
        if docstring_lines:
             docstring_lines.append("") # Blank line
        docstring_lines.append("Args:")
        for doc in param_docs:
            docstring_lines.append(f"    {doc}")

    # Generate Returns documentation
    try:
        responses = operation.get("responses", {})
        # Look for 200 OK response
        success_response = responses.get("200")
        if success_response:
            content_json = success_response.get("content", {}).get("application/json", {})
            resp_schema = content_json.get("schema", {})
            
            # Navigate schema to find data property
            data_schema = None
            if "allOf" in resp_schema:
                for sub_schema in resp_schema["allOf"]:
                    if "properties" in sub_schema and "data" in sub_schema["properties"]:
                        data_schema = sub_schema["properties"]["data"]
                        break
            elif "properties" in resp_schema and "data" in resp_schema["properties"]:
                 data_schema = resp_schema["properties"]["data"]
                 
            if data_schema:
                docstring_lines.append("")
                docstring_lines.append("Returns:")
                
                data_schema = resolve_ref(data_schema, root)
                
                if data_schema.get("type") != "object":
                    # Simple type
                    py_type = get_python_type(data_schema, root, is_docstring=True)
                    desc = data_schema.get("description", "")
                    docstring_lines.append(f"    {desc} ({py_type})")
                else:
                    # Object properties
                    resp_props = data_schema.get("properties", {})
                    for prop_name, prop_schema in resp_props.items():
                        prop_schema = resolve_ref(prop_schema, root)
                        py_type = get_python_type(prop_schema, root, is_docstring=True)
                        description = prop_schema.get("description", "")
                        if "enum" in prop_schema:
                             enums = [f'"{e}"' if isinstance(e, str) else str(e) for e in prop_schema["enum"]]
                             description += f" ({' | '.join(enums)})"
                        
                        docstring_lines.append(f"    {prop_name} ({py_type}): {description}")
    except Exception as e:
        # If any error occurs during return doc generation, just skip it
        pass
    
    if docstring_lines:
        if len(docstring_lines) == 1:
             body.append(f'        """{docstring_lines[0]}"""')
        else:
             body.append('        """')
             for line in docstring_lines:
                 body.append(f'        {line}')
             body.append('        """')
    
    # Special logic for message conversion
    if "message" in call_args:
        body.append('        if isinstance(message, str):')
        body.append('            message = [Text(message)]')

    # Construct params dict
    dict_items = []
    for arg in call_args:
        dict_items.append(f'"{arg}": {arg}')
    
    dict_str = ", ".join(dict_items)
    if len(dict_items) > 1:
        # formatting for multiple args
        body.append(f'        return await self.call_api("{operation_id}", {{')
        for arg in call_args:
             body.append(f'            "{arg}": {arg},')
        body.append('        })')
    else:
        body.append(f'        return await self.call_api("{operation_id}", {{{dict_str}}})')

    return "\n".join(body)

def main():
    if os.path.exists("openapi.json"):
        path = "openapi.json"
    elif os.path.exists("../openapi.json"):
        path = "../openapi.json"
    else:
        print("openapi.json not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    paths = data.get("paths", {})
    root = data
    
    methods = []
    for path, path_item in paths.items():
        if path.startswith("/api/"):
            method_code = generate_method(path, path_item, root)
            if method_code:
                methods.append(method_code)
                
    content = HEADER + "\n\n" + "\n\n".join(methods) + "\n"
    
    # Write to milkypy/client.py
    output_path = "milkypy/client.py"
    if not os.path.exists("milkypy") and os.path.exists("../milkypy"):
         output_path = "../milkypy/client.py"
         
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Generated {output_path}")

if __name__ == "__main__":
    main()
