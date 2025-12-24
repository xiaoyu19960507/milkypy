import json
import os
from typing import Dict, List, Any

# Static content
HEADER = """# MilkyPy 数据结构参考

本页面详细列出了 MilkyPy 中使用的核心数据结构、消息段及其 JSON 字段。所有的结构均为原始的 `dict`，你可以直接根据字段名进行访问。

---

## 核心实体 (Entities)

核心实体是 API 返回或事件推送中常见的复合 JSON 对象。
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
        return current
    return schema

def get_python_type(schema, root):
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]

    schema = resolve_ref(schema, root)
    type_name = schema.get("type")
    
    if type_name == "array":
        # If items is a ref, we can say list[dict] or just list
        items = schema.get("items", {})
        if "$ref" in items:
            ref_name = items["$ref"].split("/")[-1]
            return f"List[{ref_name}]"
        if "allOf" in items and len(items["allOf"]) == 1 and "$ref" in items["allOf"][0]:
            ref_name = items["allOf"][0]["$ref"].split("/")[-1]
            return f"List[{ref_name}]"
        
        return "list"

    if "allOf" in schema and len(schema["allOf"]) == 1:
        return get_python_type(schema["allOf"][0], root)
    
    return TYPE_MAPPING.get(type_name, "Any")

def get_field_description(prop_name, prop_schema, root):
    prop_schema = resolve_ref(prop_schema, root)
    desc = prop_schema.get("description", "")
    
    # Enrich description with enum values or sub-fields if simple
    if "enum" in prop_schema:
        enums = [f"`{e}`" for e in prop_schema["enum"]]
        desc += f" ({', '.join(enums)})"
        
    return desc

def generate_table(title, schema_name, schema, root):
    lines = []
    lines.append(f"### `{schema_name}` ({title})")
    
    description = schema.get("description", "")
    if description and description != title and description != schema_name:
         lines.append(f"{description}\n")

    # Handle OneOf (Discriminated Unions)
    if "oneOf" in schema:
        # Check if it's a discriminated union
        options = [resolve_ref(opt, root) for opt in schema["oneOf"]]
        if not options:
            return ""
            
        # 1. Identify common properties (intersection of keys)
        # Note: 'type' is often the discriminator and present in all, but its value differs (enum)
        common_keys = set(options[0].get("properties", {}).keys())
        for opt in options[1:]:
            common_keys &= set(opt.get("properties", {}).keys())
        
        # We need to distinguish between "truly common" (same schema) and "discriminator" (same key, different enum)
        truly_common_keys = []
        discriminator_key = None
        
        for key in common_keys:
            # Check if all options have the same schema for this key
            # We compare JSON string representation of resolved schemas
            first_prop = resolve_ref(options[0]["properties"][key], root)
            first_schema_str = json.dumps(first_prop, sort_keys=True)
            
            is_same_schema = True
            for opt in options[1:]:
                prop = resolve_ref(opt["properties"][key], root)
                if json.dumps(prop, sort_keys=True) != first_schema_str:
                    is_same_schema = False
                    break
            
            if is_same_schema:
                # If identical schema, it's a common property
                # (Even if it's a discriminator with same value? Unlikely for discriminator)
                truly_common_keys.append(key)
            else:
                # Schemas differ. Check if it's a discriminator (different enum values)
                is_discriminator = True
                for opt in options:
                    prop = resolve_ref(opt["properties"][key], root)
                    if "enum" not in prop or len(prop["enum"]) != 1:
                        is_discriminator = False
                        break
                
                if is_discriminator:
                    discriminator_key = key
                # Else: it's a specific property that happens to share the key (e.g. 'data' in segments)
        
        truly_common_keys.sort()
        
        if truly_common_keys or discriminator_key:
             lines.append("这是一个联合类型。所有类型均包含以下基础字段：")
             for prop in truly_common_keys:
                 # Use schema from first option as representative
                 prop_schema = options[0]["properties"][prop]
                 p_type = get_python_type(prop_schema, root)
                 desc = get_field_description(prop, prop_schema, root)
                 lines.append(f"- `{prop}`: {desc} ({p_type})")
             
             if discriminator_key:
                 # Collect all possible values
                 all_values = []
                 for opt in options:
                     all_values.extend(opt["properties"][discriminator_key]["enum"])
                 lines.append(f"- `{discriminator_key}`: 类型标识 (`{'`, `'.join(all_values)}`)")
             
             lines.append("")
        
        lines.append("包含以下变体：")
        lines.append("")
        
        for opt in options:
            # Determine variant name (from discriminator value or title)
            variant_name = "Unknown"
            variant_desc = opt.get("title", "")
            
            if discriminator_key:
                variant_name = opt["properties"][discriminator_key]["enum"][0]
                if variant_desc == variant_name: variant_desc = "" # Don't repeat if title is same as value
            else:
                variant_name = opt.get("title", "Variant")
            
            lines.append(f"#### `{variant_name}`" + (f" ({variant_desc})" if variant_desc else ""))
            
            # List specific properties
            specific_props = opt.get("properties", {})
            required_props = opt.get("required", [])
            
            # Check if this variant has a 'data' field that is an object (like Segments)
            # If so, we might want to expand it.
            
            doc_lines = []
            data_expanded = False
            
            for p, p_sch in specific_props.items():
                if p in truly_common_keys or p == discriminator_key:
                    continue
                
                p_type = get_python_type(p_sch, root)
                
                # Special handling for 'data' in segments: expand it
                if p == "data" and p_type == "dict":
                     data_props = p_sch.get("properties", {})
                     data_required = p_sch.get("required", [])
                     
                     # Fallback if no properties directly (could be ref?)
                     if not data_props and "$ref" in p_sch:
                         resolved_data = resolve_ref(p_sch, root)
                         data_props = resolved_data.get("properties", {})
                         data_required = resolved_data.get("required", [])

                     if data_props:
                         data_repr_parts = []
                         inner_lines = []
                         for dp, dp_sch in data_props.items():
                             dp_type = get_python_type(dp_sch, root)
                             data_repr_parts.append(f'"{dp}": {dp_type}')
                             dp_desc = get_field_description(dp, dp_sch, root)
                             
                             if dp not in data_required:
                                 dp_desc = f"{dp_desc} (可选)" if dp_desc else "(可选)"
                                 
                             if dp_desc:
                                 inner_lines.append(f"    - `{dp}`: {dp_desc}")
                         
                         data_repr = "{" + ", ".join(data_repr_parts) + "}"
                         doc_lines.append(f"- **data**: `{data_repr}`")
                         doc_lines.extend(inner_lines)
                         data_expanded = True
                         continue

                desc = get_field_description(p, p_sch, root)
                if p not in required_props:
                    desc = f"{desc} (可选)" if desc else "(可选)"
                    
                doc_lines.append(f"- `{p}`: {desc} ({p_type})")
            
            if not doc_lines and not data_expanded:
                lines.append("无特定字段。")
            else:
                lines.extend(doc_lines)
            
            lines.append("")
            
        return "\n".join(lines)

    # Standard Object
    lines.append("| 字段名 | 类型 | 说明 |")
    lines.append("| :--- | :--- | :--- |")
    
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    
    # If using allOf (e.g. FriendEntity -> FriendCategoryEntity), merge props
    if "allOf" in schema:
        for sub in schema["allOf"]:
            sub_schema = resolve_ref(sub, root)
            if "properties" in sub_schema:
                props.update(sub_schema["properties"])
            if "required" in sub_schema:
                required.update(sub_schema["required"])
    
    for prop_name, prop_schema in props.items():
        p_type = get_python_type(prop_schema, root)
        desc = get_field_description(prop_name, prop_schema, root)
        
        if prop_name not in required:
            desc = f"{desc} (可选)" if desc else "(可选)"
            
        lines.append(f"| `{prop_name}` | `{p_type}` | {desc} |")
        
    lines.append("")
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
        
    root = data
    schemas = data.get("components", {}).get("schemas", {})
    
    # Dynamic classification based on naming patterns
    entities = []
    message_structures = []
    message_segments = []

    for name in schemas:
        # Exclude API inputs/outputs and technical wrappers
        if name.startswith("Api_") or name in ["Event", "ApiResponse", "ApiEmptyObject"]:
            continue
            
        if "Segment" in name:
            message_segments.append(name)
        elif name.endswith("Message") and (name.startswith("Incoming") or name.startswith("Outgoing")):
            message_structures.append(name)
        else:
            entities.append(name)

    # Sort for deterministic output
    entities.sort()
    message_structures.sort()
    message_segments.sort()

    content = [HEADER]
    
    # Entities
    for name in entities:
        if name in schemas:
            schema = schemas[name]
            title = schema.get("title", name)
            doc = generate_table(title, name, schema, root)
            content.append(doc)
            
    content.append("---\n")
    content.append("## 消息结构 (Message Structures)\n")
    
    # Message Structures
    for name in message_structures:
         if name in schemas:
            schema = schemas[name]
            title = schema.get("title", name)
            doc = generate_table(title, name, schema, root)
            content.append(doc)
            
    content.append("---\n")
    content.append("## 消息段 (Message Segments)\n")
    
    # Segments
    # Usually we want to show IncomingSegment as it defines the structure
    # But to be generic, we just dump whatever is in message_segments list
    for name in message_segments:
        if name in schemas:
            schema = schemas[name]
            title = schema.get("title", name)
            doc = generate_table(title, name, schema, root)
            content.append(doc)
    
    final_md = "\n".join(content)
    
    output_path = "docs/structs.md"
    if not os.path.exists("docs") and os.path.exists("../docs"):
         output_path = "../docs/structs.md"
         
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_md)
        
    print(f"Generated {output_path}")

if __name__ == "__main__":
    main()
