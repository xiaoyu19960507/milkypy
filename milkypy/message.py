from typing import List, Optional

def Text(text: str) -> dict:
    """
    构造文本消息段 (Text Segment)
    
    Args:
        text (str): 文本内容
        
    Returns:
        dict: {"type": "text", "data": {"text": text}}
    """
    return {"type": "text", "data": {"text": text}}

def Mention(user_id: int) -> dict:
    """
    构造提及消息段 (Mention Segment)
    
    Args:
        user_id (int): 提及的 QQ 号 (int64)
        
    Returns:
        dict: {"type": "mention", "data": {"user_id": user_id}}
    """
    return {"type": "mention", "data": {"user_id": user_id}}

def MentionAll() -> dict:
    """
    构造提及全体消息段 (Mention All Segment)
    
    Returns:
        dict: {"type": "mention_all", "data": {}}
    """
    return {"type": "mention_all", "data": {}}

def Face(face_id: str) -> dict:
    """
    构造表情消息段 (Face Segment)
    
    Args:
        face_id (str): 表情 ID
        
    Returns:
        dict: {"type": "face", "data": {"face_id": face_id}}
    """
    return {"type": "face", "data": {"face_id": face_id}}

def Reply(message_seq: int) -> dict:
    """
    构造回复消息段 (Reply Segment)
    
    Args:
        message_seq (int): 被引用的消息序列号 (int64)
        
    Returns:
        dict: {"type": "reply", "data": {"message_seq": message_seq}}
    """
    return {"type": "reply", "data": {"message_seq": message_seq}}

def Image(uri: str, sub_type: str = "normal", summary: Optional[str] = None) -> dict:
    """
    构造图片消息段 (Image Segment)
    
    Args:
        uri (str): 文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式
        sub_type (str, 可选): 图片类型 ("normal" | "sticker")。默认为 "normal"。
        summary (str, 可选): 图片预览文本。默认为 None。
        
    Returns:
        dict: {"type": "image", "data": {...}}
    """
    data = {"uri": uri, "sub_type": sub_type}
    if summary:
        data["summary"] = summary
    return {"type": "image", "data": data}

def Record(uri: str) -> dict:
    """
    构造语音消息段 (Record Segment)
    
    Args:
        uri (str): 文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式
        
    Returns:
        dict: {"type": "record", "data": {"uri": uri}}
    """
    return {"type": "record", "data": {"uri": uri}}

def Video(uri: str, thumb_uri: Optional[str] = None) -> dict:
    """
    构造视频消息段 (Video Segment)
    
    Args:
        uri (str): 文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式
        thumb_uri (str, 可选): 封面图片 URI。默认为 None。
        
    Returns:
        dict: {"type": "video", "data": {...}}
    """
    data = {"uri": uri}
    if thumb_uri:
        data["thumb_uri"] = thumb_uri
    return {"type": "video", "data": data}

def Forward(messages: List[dict]) -> dict:
    """
    构造合并转发消息段 (Forward Segment)
    
    Args:
        messages (List[dict]): 合并转发消息段列表 (OutgoingForwardedMessage[])
        
    Returns:
        dict: {"type": "forward", "data": {"messages": messages}}
    """
    return {"type": "forward", "data": {"messages": messages}}
