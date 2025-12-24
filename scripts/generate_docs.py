import json
import os
from typing import Dict, List, Any

# Static content
HEADER = """# MilkyPy API 参考文档

本页面详细列出了 `MilkyClient` 中可用的所有 API 方法及其参数。所有的 API 均采用异步 (`async`) 调用。

> [!TIP]
> 所有的 API 返回值均为原始的 `dict` 或 `list`，其字段结构与 Milky 协议文档保持完全一致。详细说明请参阅 [数据结构参考](structs.md)。

## 核心生命周期

### `MilkyClient(host, port=3010, token=None, api_port=None, event_port=None)`
初始化客户端。
- **参数**:
    - `host`: 协议端 IP 地址。
    - `port`: 默认端口号，默认为 `3010`。若未指定 `api_port` 或 `event_port`，则统一使用此端口。
    - `token`: 鉴权 Token（可选）。
    - `api_port`: 单独指定 HTTP API 的端口（可选）。
    - `event_port`: 单独指定 WebSocket 事件推送的端口（可选）。

### `run()`
启动客户端并建立 WebSocket 连接。这是一个阻塞调用，通常作为程序的入口。
- **示例**: `await bot.run()`

---
"""

FOOTER = """
## 低级调用

### `call_api(action: str, params: dict = None)`
调用 Milky 协议定义的任意 API（别名方法，等同于 `call_api_http`）。

### `call_api_http(action: str, params: dict = None)`
通过 HTTP 直接调用 Milky 协议定义的任意 API。
- **示例**: `await bot.call_api_http("get_cookies", {"domain": "qq.com"})`

---

## 消息段辅助函数 (Message Segments)

MilkyPy 提供了一系列辅助函数来帮助你构造消息段。你可以将这些函数生成的对象组合成一个数组发送。

### 常用函数
- `Text(content: str)`: 构造纯文本消息段。
- `Mention(user_id: int)`: @ 某人。
- `MentionAll()`: @ 全体成员。
- `Face(face_id: str)`: 添加 QQ 表情。
- `Reply(message_seq: int)`: 回复某条消息。
- `Image(uri: str, sub_type: str = "normal", summary: str = None)`: 构造图片消息段。支持 `file://` (本地路径), `http://` (网络链接), `base64://` (Base64 编码)。`sub_type` 可选 `normal` 或 `sticker`。
- `Record(uri: str)`: 构造语音消息段。
- `Video(uri: str, thumb_uri: str = None)`: 构造视频消息段。
- `Forward(messages: List[dict])`: 构造合并转发消息段。

### 静态辅助工具 (`Message`)
- `Message.extract_text(segments: list)`: 从接收到的消息段列表中提取出所有的纯文本内容。
"""

TYPE_MAPPING = {
    "string": "str",
    "integer": "int",
    "boolean": "bool",
    "array": "list",
    "object": "dict",
}

def resolve_ref(schema, root):
    if "$ref" in schema:
        ref_path = schema["$ref"].split("/")
        current = root
        for part in ref_path[1:]:
            current = current[part]
        return resolve_ref(current, root)
    return schema

def get_python_type(schema, root):
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
        
    if "allOf" in schema and len(schema["allOf"]) == 1:
        return get_python_type(schema["allOf"][0], root)

    schema = resolve_ref(schema, root)
    type_name = schema.get("type")
    
    if type_name == "array":
        items = schema.get("items", {})
        item_type = get_python_type(items, root)
        return f"List[{item_type}]" if item_type != "Any" else "list"
    
    return TYPE_MAPPING.get(type_name, "Any")

def get_return_description(operation, root):
    responses = operation.get("responses", {})
    success = responses.get("200", {})
    content = success.get("content", {}).get("application/json", {})
    schema = content.get("schema", {})
    
    # Usually schema is allOf [ApiResponse, {properties: {data: ...}}]
    # We want to find the data schema
    
    if "allOf" in schema:
        for sub_schema in schema["allOf"]:
            sub = resolve_ref(sub_schema, root)
            if "properties" in sub and "data" in sub["properties"]:
                data_schema = sub["properties"]["data"]
                if not data_schema:
                    continue
                return describe_schema(data_schema, root)
                
    return ""

def describe_schema(schema, root):
    # Get type first (could be ref name)
    p_type_main = get_python_type(schema, root)
    
    resolved = resolve_ref(schema, root)
    type_name = resolved.get("type")
    
    if type_name == "object":
        props = resolved.get("properties", {})
        if not props:
            # If it's a ref object but no properties listed (maybe because it's just a type def)
             # But if get_python_type returned a Name, we might use it.
             if p_type_main != "dict" and p_type_main != "Any":
                  if p_type_main == "ApiEmptyObject":
                      return "空字典。"
                  return f"包含 `{p_type_main}` 的字典。"
             return "包含响应数据的字典。"
            
        lines = []
        lines.append(f"包含以下字段的字典：")
        for prop_name, prop_schema in props.items():
            p_type = get_python_type(prop_schema, root)
            
            resolved_prop = resolve_ref(prop_schema, root)
            desc = resolved_prop.get("description", "")
            
            line = f"    - `{prop_name}`: "
            if desc:
                line += f"{desc} ({p_type})"
            else:
                line += f"({p_type})"
            lines.append(line)
        return "\n".join(lines)
        
    elif type_name == "array":
        items = resolved.get("items", {})
        item_type = get_python_type(items, root)
        return f"包含 `{item_type}` 列表的字典。"
        
    return f"返回 {type_name} 类型的数据。"

def generate_method_doc(path, path_item, root):
    if "post" not in path_item:
        return ""
    
    operation = path_item["post"]
    operation_id = operation.get("operationId") or path.split("/")[-1]
    summary = operation.get("summary", "")
    
    # Inputs
    req_body = operation.get("requestBody", {})
    content = req_body.get("content", {}).get("application/json", {})
    schema = content.get("schema", {})
    schema = resolve_ref(schema, root)
    
    props = schema.get("properties", {})
    required = schema.get("required", [])
    
    # Sort props
    sorted_props = []
    for p in props:
        if p in required: sorted_props.append(p)
    for p in props:
        if p not in required: sorted_props.append(p)
        
    param_lines = []
    sig_args = []
    
    for prop_name in sorted_props:
        prop_schema = props[prop_name]
        
        py_type = get_python_type(prop_schema, root)
        
        # Special handling for message
        if prop_name == "message" and "List" in py_type:
            py_type = "Union[str, List[dict]]"

        resolved_prop = resolve_ref(prop_schema, root)
        desc = resolved_prop.get("description", "")
        
        # Add enums to description
        if "enum" in resolved_prop:
            enums = [f'"{e}"' if isinstance(e, str) else str(e) for e in resolved_prop["enum"]]
            desc += f" ({' | '.join(enums)})"
        
        # Sig
        if prop_name in required:
            sig_args.append(f"{prop_name}: {py_type}")
        else:
            default_v = resolved_prop.get("default", "None")
            
            if default_v != "None":
                if isinstance(default_v, str): default_v = f'"{default_v}"'
                elif isinstance(default_v, bool): default_v = str(default_v)
            
            sig_args.append(f"{prop_name}: {py_type} = {default_v}")
            
        # Doc
        line = f"    - `{prop_name}`: "
        if desc:
            line += f"{desc} ({py_type})"
        else:
            line += f"({py_type})"
        param_lines.append(line)
        
    sig_str = ", ".join(sig_args)
    
    # Return value
    return_desc = get_return_description(operation, root)
    
    # Markdown construction
    lines = []
    lines.append(f"### `{operation_id}({sig_str})`")
    lines.append(f"{summary}")
    
    if param_lines:
        lines.append(f"- **参数**:")
        lines.extend(param_lines)
        
    if return_desc:
        lines.append(f"- **返回**: {return_desc}")
        
    lines.append("") # Empty line
    return "\n".join(lines)

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
    
    # Collect all methods
    method_map = {}
    methods_by_tag = {}
    
    for path, path_item in paths.items():
        if path.startswith("/api/"):
            op_id = path.split("/")[-1]
            if "post" in path_item:
                op = path_item["post"]
                if "operationId" in op:
                    op_id = op["operationId"]
                
                method_map[op_id] = (path, path_item)
                
                tags = op.get("tags", ["未分类接口"])
                main_tag = tags[0] if tags else "未分类接口"
                
                if main_tag not in methods_by_tag:
                    methods_by_tag[main_tag] = []
                methods_by_tag[main_tag].append(op_id)
            
    # Generate content
    content = [HEADER]
    
    # Process all tags in alphabetical order
    for tag in sorted(methods_by_tag.keys()):
        content.append(f"## {tag}\n")
        methods = sorted(methods_by_tag[tag])
        for method_name in methods:
            path, path_item = method_map[method_name]
            doc = generate_method_doc(path, path_item, root)
            content.append(doc)
        content.append("---\n")
            
    content.append(FOOTER)
    
    final_md = "\n".join(content)
    
    output_path = "docs/api.md"
    if not os.path.exists("docs") and os.path.exists("../docs"):
         output_path = "../docs/api.md"
         
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_md)
        
    print(f"Generated {output_path}")

if __name__ == "__main__":
    main()
