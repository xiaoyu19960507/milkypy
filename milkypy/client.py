import asyncio
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
            logger.warning(f"Invalid message format: {message}")
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
        """运行客户端"""
        await self.connect()

    # Helper methods for common APIs

    async def get_login_info(self) -> Dict[str, Any]:
        """
        获取登录信息
        
        Returns:
            uin (int): 登录 QQ 号
            nickname (str): 登录昵称
        """
        return await self.call_api("get_login_info", {})

    async def get_impl_info(self) -> Dict[str, Any]:
        """
        获取协议端信息
        
        Returns:
            impl_name (str): 协议端名称
            impl_version (str): 协议端版本
            qq_protocol_version (str): 协议端使用的 QQ 协议版本
            qq_protocol_type (str): 协议端使用的 QQ 协议平台 ("windows" | "linux" | "macos" | "android_pad" | "android_phone" | "ipad" | "iphone" | "harmony" | "watch")
            milky_version (str): 协议端实现的 Milky 协议版本，目前为 "1.0"
        """
        return await self.call_api("get_impl_info", {})

    async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户个人信息
        
        Args:
            user_id: 用户 QQ 号
        
        Returns:
            nickname (str): 昵称
            qid (str): QID
            age (int): 年龄
            sex (str): 性别 ("male" | "female" | "unknown")
            remark (str): 备注
            bio (str): 个性签名
            level (int): QQ 等级
            country (str): 国家或地区
            city (str): 城市
            school (str): 学校
        """
        return await self.call_api("get_user_profile", {"user_id": user_id})

    async def get_friend_list(self, no_cache: bool = False) -> Dict[str, Any]:
        """
        获取好友列表
        
        Args:
            no_cache: 是否强制不使用缓存
        
        Returns:
            friends (List[FriendEntity]): 好友列表
        """
        return await self.call_api("get_friend_list", {"no_cache": no_cache})

    async def get_friend_info(self, user_id: int, no_cache: bool = False) -> Dict[str, Any]:
        """
        获取好友信息
        
        Args:
            user_id: 好友 QQ 号
            no_cache: 是否强制不使用缓存
        
        Returns:
            friend (FriendEntity): 好友信息
        """
        return await self.call_api("get_friend_info", {
            "user_id": user_id,
            "no_cache": no_cache,
        })

    async def get_group_list(self, no_cache: bool = False) -> Dict[str, Any]:
        """
        获取群列表
        
        Args:
            no_cache: 是否强制不使用缓存
        
        Returns:
            groups (List[GroupEntity]): 群列表
        """
        return await self.call_api("get_group_list", {"no_cache": no_cache})

    async def get_group_info(self, group_id: int, no_cache: bool = False) -> Dict[str, Any]:
        """
        获取群信息
        
        Args:
            group_id: 群号
            no_cache: 是否强制不使用缓存
        
        Returns:
            group (GroupEntity): 群信息
        """
        return await self.call_api("get_group_info", {
            "group_id": group_id,
            "no_cache": no_cache,
        })

    async def get_group_member_list(self, group_id: int, no_cache: bool = False) -> Dict[str, Any]:
        """
        获取群成员列表
        
        Args:
            group_id: 群号
            no_cache: 是否强制不使用缓存
        
        Returns:
            members (List[GroupMemberEntity]): 群成员列表
        """
        return await self.call_api("get_group_member_list", {
            "group_id": group_id,
            "no_cache": no_cache,
        })

    async def get_group_member_info(self, group_id: int, user_id: int, no_cache: bool = False) -> Dict[str, Any]:
        """
        获取群成员信息
        
        Args:
            group_id: 群号
            user_id: 群成员 QQ 号
            no_cache: 是否强制不使用缓存
        
        Returns:
            member (GroupMemberEntity): 群成员信息
        """
        return await self.call_api("get_group_member_info", {
            "group_id": group_id,
            "user_id": user_id,
            "no_cache": no_cache,
        })

    async def get_cookies(self, domain: str) -> Dict[str, Any]:
        """
        获取 Cookies
        
        Args:
            domain: 需要获取 Cookies 的域名
        
        Returns:
            cookies (str): 域名对应的 Cookies 字符串
        """
        return await self.call_api("get_cookies", {"domain": domain})

    async def get_csrf_token(self) -> Dict[str, Any]:
        """
        获取 CSRF Token
        
        Returns:
            csrf_token (str): CSRF Token
        """
        return await self.call_api("get_csrf_token", {})

    async def send_private_message(self, user_id: int, message: Union[str, List[dict]]) -> Dict[str, Any]:
        """
        发送私聊消息
        
        Args:
            user_id: 好友 QQ 号
            message: 消息内容
        
        Returns:
            message_seq (int): 消息序列号
            time (int): 消息发送时间
        """
        if isinstance(message, str):
            message = [Text(message)]
        return await self.call_api("send_private_message", {
            "user_id": user_id,
            "message": message,
        })

    async def send_group_message(self, group_id: int, message: Union[str, List[dict]]) -> Dict[str, Any]:
        """
        发送群聊消息
        
        Args:
            group_id: 群号
            message: 消息内容
        
        Returns:
            message_seq (int): 消息序列号
            time (int): 消息发送时间
        """
        if isinstance(message, str):
            message = [Text(message)]
        return await self.call_api("send_group_message", {
            "group_id": group_id,
            "message": message,
        })

    async def recall_private_message(self, user_id: int, message_seq: int) -> Dict[str, Any]:
        """
        撤回私聊消息
        
        Args:
            user_id: 好友 QQ 号
            message_seq: 消息序列号
        
        Returns:
        """
        return await self.call_api("recall_private_message", {
            "user_id": user_id,
            "message_seq": message_seq,
        })

    async def recall_group_message(self, group_id: int, message_seq: int) -> Dict[str, Any]:
        """
        撤回群聊消息
        
        Args:
            group_id: 群号
            message_seq: 消息序列号
        
        Returns:
        """
        return await self.call_api("recall_group_message", {
            "group_id": group_id,
            "message_seq": message_seq,
        })

    async def get_message(self, message_scene: str, peer_id: int, message_seq: int) -> Dict[str, Any]:
        """
        获取消息
        
        Args:
            message_scene: 消息场景 ("friend" | "group" | "temp")
            peer_id: 好友 QQ 号或群号
            message_seq: 消息序列号
        
        Returns:
            message (IncomingMessage): 消息内容
        """
        return await self.call_api("get_message", {
            "message_scene": message_scene,
            "peer_id": peer_id,
            "message_seq": message_seq,
        })

    async def get_history_messages(self, message_scene: str, peer_id: int, start_message_seq: Optional[int] = None, limit: int = 20) -> Dict[str, Any]:
        """
        获取历史消息列表
        
        Args:
            message_scene: 消息场景 ("friend" | "group" | "temp")
            peer_id: 好友 QQ 号或群号
            start_message_seq: 起始消息序列号，由此开始从新到旧查询，不提供则从最新消息开始
            limit: 期望获取到的消息数量，最多 30 条
        
        Returns:
            messages (List[IncomingMessage]): 获取到的消息（message_seq 升序排列），部分消息可能不存在，如撤回的消息
            next_message_seq (int): 下一页起始消息序列号
        """
        return await self.call_api("get_history_messages", {
            "message_scene": message_scene,
            "peer_id": peer_id,
            "start_message_seq": start_message_seq,
            "limit": limit,
        })

    async def get_resource_temp_url(self, resource_id: str) -> Dict[str, Any]:
        """
        获取临时资源链接
        
        Args:
            resource_id: 资源 ID
        
        Returns:
            url (str): 临时资源链接
        """
        return await self.call_api("get_resource_temp_url", {"resource_id": resource_id})

    async def get_forwarded_messages(self, forward_id: str) -> Dict[str, Any]:
        """
        获取合并转发消息内容
        
        Args:
            forward_id: 转发消息 ID
        
        Returns:
            messages (List[IncomingForwardedMessage]): 转发消息内容
        """
        return await self.call_api("get_forwarded_messages", {"forward_id": forward_id})

    async def mark_message_as_read(self, message_scene: str, peer_id: int, message_seq: int) -> Dict[str, Any]:
        """
        标记消息为已读
        
        Args:
            message_scene: 消息场景 ("friend" | "group" | "temp")
            peer_id: 好友 QQ 号或群号
            message_seq: 标为已读的消息序列号，该消息及更早的消息将被标记为已读
        
        Returns:
        """
        return await self.call_api("mark_message_as_read", {
            "message_scene": message_scene,
            "peer_id": peer_id,
            "message_seq": message_seq,
        })

    async def send_friend_nudge(self, user_id: int, is_self: bool = False) -> Dict[str, Any]:
        """
        发送好友戳一戳
        
        Args:
            user_id: 好友 QQ 号
            is_self: 是否戳自己
        
        Returns:
        """
        return await self.call_api("send_friend_nudge", {
            "user_id": user_id,
            "is_self": is_self,
        })

    async def send_profile_like(self, user_id: int, count: int = 1) -> Dict[str, Any]:
        """
        发送名片点赞
        
        Args:
            user_id: 好友 QQ 号
            count: 点赞数量
        
        Returns:
        """
        return await self.call_api("send_profile_like", {
            "user_id": user_id,
            "count": count,
        })

    async def get_friend_requests(self, limit: int = 20, is_filtered: bool = False) -> Dict[str, Any]:
        """
        获取好友请求列表
        
        Args:
            limit: 获取的最大请求数量
            is_filtered: `true` 表示只获取被过滤（由风险账号发起）的通知，`false` 表示只获取未被过滤的通知
        
        Returns:
            requests (List[FriendRequest]): 好友请求列表
        """
        return await self.call_api("get_friend_requests", {
            "limit": limit,
            "is_filtered": is_filtered,
        })

    async def accept_friend_request(self, initiator_uid: str, is_filtered: bool = False) -> Dict[str, Any]:
        """
        同意好友请求
        
        Args:
            initiator_uid: 请求发起者 UID
            is_filtered: 是否是被过滤的请求
        
        Returns:
        """
        return await self.call_api("accept_friend_request", {
            "initiator_uid": initiator_uid,
            "is_filtered": is_filtered,
        })

    async def reject_friend_request(self, initiator_uid: str, is_filtered: bool = False, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        拒绝好友请求
        
        Args:
            initiator_uid: 请求发起者 UID
            is_filtered: 是否是被过滤的请求
            reason: 拒绝理由
        
        Returns:
        """
        return await self.call_api("reject_friend_request", {
            "initiator_uid": initiator_uid,
            "is_filtered": is_filtered,
            "reason": reason,
        })

    async def set_group_name(self, group_id: int, new_group_name: str) -> Dict[str, Any]:
        """
        设置群名称
        
        Args:
            group_id: 群号
            new_group_name: 新群名称
        
        Returns:
        """
        return await self.call_api("set_group_name", {
            "group_id": group_id,
            "new_group_name": new_group_name,
        })

    async def set_group_avatar(self, group_id: int, image_uri: str) -> Dict[str, Any]:
        """
        设置群头像
        
        Args:
            group_id: 群号
            image_uri: 头像文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式
        
        Returns:
        """
        return await self.call_api("set_group_avatar", {
            "group_id": group_id,
            "image_uri": image_uri,
        })

    async def set_group_member_card(self, group_id: int, user_id: int, card: str) -> Dict[str, Any]:
        """
        设置群名片
        
        Args:
            group_id: 群号
            user_id: 被设置的群成员 QQ 号
            card: 新群名片
        
        Returns:
        """
        return await self.call_api("set_group_member_card", {
            "group_id": group_id,
            "user_id": user_id,
            "card": card,
        })

    async def set_group_member_special_title(self, group_id: int, user_id: int, special_title: str) -> Dict[str, Any]:
        """
        设置群成员专属头衔
        
        Args:
            group_id: 群号
            user_id: 被设置的群成员 QQ 号
            special_title: 新专属头衔
        
        Returns:
        """
        return await self.call_api("set_group_member_special_title", {
            "group_id": group_id,
            "user_id": user_id,
            "special_title": special_title,
        })

    async def set_group_member_admin(self, group_id: int, user_id: int, is_set: bool = True) -> Dict[str, Any]:
        """
        设置群管理员
        
        Args:
            group_id: 群号
            user_id: 被设置的 QQ 号
            is_set: 是否设置为管理员，`false` 表示取消管理员
        
        Returns:
        """
        return await self.call_api("set_group_member_admin", {
            "group_id": group_id,
            "user_id": user_id,
            "is_set": is_set,
        })

    async def set_group_member_mute(self, group_id: int, user_id: int, duration: int = 0) -> Dict[str, Any]:
        """
        设置群成员禁言
        
        Args:
            group_id: 群号
            user_id: 被设置的 QQ 号
            duration: 禁言持续时间（秒），设为 `0` 为取消禁言
        
        Returns:
        """
        return await self.call_api("set_group_member_mute", {
            "group_id": group_id,
            "user_id": user_id,
            "duration": duration,
        })

    async def set_group_whole_mute(self, group_id: int, is_mute: bool = True) -> Dict[str, Any]:
        """
        设置群全员禁言
        
        Args:
            group_id: 群号
            is_mute: 是否开启全员禁言，`false` 表示取消全员禁言
        
        Returns:
        """
        return await self.call_api("set_group_whole_mute", {
            "group_id": group_id,
            "is_mute": is_mute,
        })

    async def kick_group_member(self, group_id: int, user_id: int, reject_add_request: bool = False) -> Dict[str, Any]:
        """
        踢出群成员
        
        Args:
            group_id: 群号
            user_id: 被踢的 QQ 号
            reject_add_request: 是否拒绝加群申请，`false` 表示不拒绝
        
        Returns:
        """
        return await self.call_api("kick_group_member", {
            "group_id": group_id,
            "user_id": user_id,
            "reject_add_request": reject_add_request,
        })

    async def get_group_announcements(self, group_id: int) -> Dict[str, Any]:
        """
        获取群公告列表
        
        Args:
            group_id: 群号
        
        Returns:
            announcements (List[GroupAnnouncementEntity]): 群公告列表
        """
        return await self.call_api("get_group_announcements", {"group_id": group_id})

    async def send_group_announcement(self, group_id: int, content: str, image_uri: Optional[str] = None) -> Dict[str, Any]:
        """
        发送群公告
        
        Args:
            group_id: 群号
            content: 公告内容
            image_uri: 公告附带图像文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式
        
        Returns:
        """
        return await self.call_api("send_group_announcement", {
            "group_id": group_id,
            "content": content,
            "image_uri": image_uri,
        })

    async def delete_group_announcement(self, group_id: int, announcement_id: str) -> Dict[str, Any]:
        """
        删除群公告
        
        Args:
            group_id: 群号
            announcement_id: 公告 ID
        
        Returns:
        """
        return await self.call_api("delete_group_announcement", {
            "group_id": group_id,
            "announcement_id": announcement_id,
        })

    async def get_group_essence_messages(self, group_id: int, page_index: int, page_size: int) -> Dict[str, Any]:
        """
        获取群精华消息列表
        
        Args:
            group_id: 群号
            page_index: 页码索引，从 0 开始
            page_size: 每页包含的精华消息数量
        
        Returns:
            messages (List[GroupEssenceMessage]): 精华消息列表
            is_end (bool): 是否已到最后一页
        """
        return await self.call_api("get_group_essence_messages", {
            "group_id": group_id,
            "page_index": page_index,
            "page_size": page_size,
        })

    async def set_group_essence_message(self, group_id: int, message_seq: int, is_set: bool = True) -> Dict[str, Any]:
        """
        设置群精华消息
        
        Args:
            group_id: 群号
            message_seq: 消息序列号
            is_set: 是否设置为精华消息，`false` 表示取消精华
        
        Returns:
        """
        return await self.call_api("set_group_essence_message", {
            "group_id": group_id,
            "message_seq": message_seq,
            "is_set": is_set,
        })

    async def quit_group(self, group_id: int) -> Dict[str, Any]:
        """
        退出群
        
        Args:
            group_id: 群号
        
        Returns:
        """
        return await self.call_api("quit_group", {"group_id": group_id})

    async def send_group_message_reaction(self, group_id: int, message_seq: int, reaction: str, is_add: bool = True) -> Dict[str, Any]:
        """
        发送群消息表情回应
        
        Args:
            group_id: 群号
            message_seq: 要回应的消息序列号
            reaction: 表情 ID
            is_add: 是否添加表情，`false` 表示取消
        
        Returns:
        """
        return await self.call_api("send_group_message_reaction", {
            "group_id": group_id,
            "message_seq": message_seq,
            "reaction": reaction,
            "is_add": is_add,
        })

    async def send_group_nudge(self, group_id: int, user_id: int) -> Dict[str, Any]:
        """
        发送群戳一戳
        
        Args:
            group_id: 群号
            user_id: 被戳的群成员 QQ 号
        
        Returns:
        """
        return await self.call_api("send_group_nudge", {
            "group_id": group_id,
            "user_id": user_id,
        })

    async def get_group_notifications(self, start_notification_seq: Optional[int] = None, is_filtered: bool = False, limit: int = 20) -> Dict[str, Any]:
        """
        获取群通知列表
        
        Args:
            start_notification_seq: 起始通知序列号
            is_filtered: `true` 表示只获取被过滤（由风险账号发起）的通知，`false` 表示只获取未被过滤的通知
            limit: 获取的最大通知数量
        
        Returns:
            notifications (List[GroupNotification]): 获取到的群通知（notification_seq 降序排列），序列号不一定连续
            next_notification_seq (int): 下一页起始通知序列号
        """
        return await self.call_api("get_group_notifications", {
            "start_notification_seq": start_notification_seq,
            "is_filtered": is_filtered,
            "limit": limit,
        })

    async def accept_group_request(self, notification_seq: int, notification_type: str, group_id: int, is_filtered: bool = False) -> Dict[str, Any]:
        """
        同意入群/邀请他人入群请求
        
        Args:
            notification_seq: 请求对应的通知序列号
            notification_type: 请求对应的通知类型 ("join_request" | "invited_join_request")
            group_id: 请求所在的群号
            is_filtered: 是否是被过滤的请求
        
        Returns:
        """
        return await self.call_api("accept_group_request", {
            "notification_seq": notification_seq,
            "notification_type": notification_type,
            "group_id": group_id,
            "is_filtered": is_filtered,
        })

    async def reject_group_request(self, notification_seq: int, notification_type: str, group_id: int, is_filtered: bool = False, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        拒绝入群/邀请他人入群请求
        
        Args:
            notification_seq: 请求对应的通知序列号
            notification_type: 请求对应的通知类型 ("join_request" | "invited_join_request")
            group_id: 请求所在的群号
            is_filtered: 是否是被过滤的请求
            reason: 拒绝理由
        
        Returns:
        """
        return await self.call_api("reject_group_request", {
            "notification_seq": notification_seq,
            "notification_type": notification_type,
            "group_id": group_id,
            "is_filtered": is_filtered,
            "reason": reason,
        })

    async def accept_group_invitation(self, group_id: int, invitation_seq: int) -> Dict[str, Any]:
        """
        同意他人邀请自身入群
        
        Args:
            group_id: 群号
            invitation_seq: 邀请序列号
        
        Returns:
        """
        return await self.call_api("accept_group_invitation", {
            "group_id": group_id,
            "invitation_seq": invitation_seq,
        })

    async def reject_group_invitation(self, group_id: int, invitation_seq: int) -> Dict[str, Any]:
        """
        拒绝他人邀请自身入群
        
        Args:
            group_id: 群号
            invitation_seq: 邀请序列号
        
        Returns:
        """
        return await self.call_api("reject_group_invitation", {
            "group_id": group_id,
            "invitation_seq": invitation_seq,
        })

    async def upload_private_file(self, user_id: int, file_uri: str, file_name: str) -> Dict[str, Any]:
        """
        上传私聊文件
        
        Args:
            user_id: 好友 QQ 号
            file_uri: 文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式
            file_name: 文件名称
        
        Returns:
            file_id (str): 文件 ID
        """
        return await self.call_api("upload_private_file", {
            "user_id": user_id,
            "file_uri": file_uri,
            "file_name": file_name,
        })

    async def upload_group_file(self, group_id: int, file_uri: str, file_name: str, parent_folder_id: str = "/") -> Dict[str, Any]:
        """
        上传群文件
        
        Args:
            group_id: 群号
            file_uri: 文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式
            file_name: 文件名称
            parent_folder_id: 目标文件夹 ID
        
        Returns:
            file_id (str): 文件 ID
        """
        return await self.call_api("upload_group_file", {
            "group_id": group_id,
            "file_uri": file_uri,
            "file_name": file_name,
            "parent_folder_id": parent_folder_id,
        })

    async def get_private_file_download_url(self, user_id: int, file_id: str, file_hash: str) -> Dict[str, Any]:
        """
        获取私聊文件下载链接
        
        Args:
            user_id: 好友 QQ 号
            file_id: 文件 ID
            file_hash: 文件的 TriSHA1 哈希值
        
        Returns:
            download_url (str): 文件下载链接
        """
        return await self.call_api("get_private_file_download_url", {
            "user_id": user_id,
            "file_id": file_id,
            "file_hash": file_hash,
        })

    async def get_group_file_download_url(self, group_id: int, file_id: str) -> Dict[str, Any]:
        """
        获取群文件下载链接
        
        Args:
            group_id: 群号
            file_id: 文件 ID
        
        Returns:
            download_url (str): 文件下载链接
        """
        return await self.call_api("get_group_file_download_url", {
            "group_id": group_id,
            "file_id": file_id,
        })

    async def get_group_files(self, group_id: int, parent_folder_id: str = "/") -> Dict[str, Any]:
        """
        获取群文件列表
        
        Args:
            group_id: 群号
            parent_folder_id: 父文件夹 ID
        
        Returns:
            files (List[GroupFileEntity]): 文件列表
            folders (List[GroupFolderEntity]): 文件夹列表
        """
        return await self.call_api("get_group_files", {
            "group_id": group_id,
            "parent_folder_id": parent_folder_id,
        })

    async def move_group_file(self, group_id: int, file_id: str, parent_folder_id: str = "/", target_folder_id: str = "/") -> Dict[str, Any]:
        """
        移动群文件
        
        Args:
            group_id: 群号
            file_id: 文件 ID
            parent_folder_id: 文件所在的文件夹 ID
            target_folder_id: 目标文件夹 ID
        
        Returns:
        """
        return await self.call_api("move_group_file", {
            "group_id": group_id,
            "file_id": file_id,
            "parent_folder_id": parent_folder_id,
            "target_folder_id": target_folder_id,
        })

    async def rename_group_file(self, group_id: int, file_id: str, new_file_name: str, parent_folder_id: str = "/") -> Dict[str, Any]:
        """
        重命名群文件
        
        Args:
            group_id: 群号
            file_id: 文件 ID
            new_file_name: 新文件名称
            parent_folder_id: 文件所在的文件夹 ID
        
        Returns:
        """
        return await self.call_api("rename_group_file", {
            "group_id": group_id,
            "file_id": file_id,
            "new_file_name": new_file_name,
            "parent_folder_id": parent_folder_id,
        })

    async def delete_group_file(self, group_id: int, file_id: str) -> Dict[str, Any]:
        """
        删除群文件
        
        Args:
            group_id: 群号
            file_id: 文件 ID
        
        Returns:
        """
        return await self.call_api("delete_group_file", {
            "group_id": group_id,
            "file_id": file_id,
        })

    async def create_group_folder(self, group_id: int, folder_name: str) -> Dict[str, Any]:
        """
        创建群文件夹
        
        Args:
            group_id: 群号
            folder_name: 文件夹名称
        
        Returns:
            folder_id (str): 文件夹 ID
        """
        return await self.call_api("create_group_folder", {
            "group_id": group_id,
            "folder_name": folder_name,
        })

    async def rename_group_folder(self, group_id: int, folder_id: str, new_folder_name: str) -> Dict[str, Any]:
        """
        重命名群文件夹
        
        Args:
            group_id: 群号
            folder_id: 文件夹 ID
            new_folder_name: 新文件夹名
        
        Returns:
        """
        return await self.call_api("rename_group_folder", {
            "group_id": group_id,
            "folder_id": folder_id,
            "new_folder_name": new_folder_name,
        })

    async def delete_group_folder(self, group_id: int, folder_id: str) -> Dict[str, Any]:
        """
        删除群文件夹
        
        Args:
            group_id: 群号
            folder_id: 文件夹 ID
        
        Returns:
        """
        return await self.call_api("delete_group_folder", {
            "group_id": group_id,
            "folder_id": folder_id,
        })
