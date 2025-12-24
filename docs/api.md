# MilkyPy API 参考文档

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

## 好友 API

### `accept_friend_request(initiator_uid: str, is_filtered: bool = False)`
同意好友请求
- **参数**:
    - `initiator_uid`: 请求发起者 UID (str)
    - `is_filtered`: 是否是被过滤的请求 (bool)
- **返回**: 空字典。

### `get_friend_requests(limit: int = 20, is_filtered: bool = False)`
获取好友请求列表
- **参数**:
    - `limit`: 获取的最大请求数量 (int)
    - `is_filtered`: `true` 表示只获取被过滤（由风险账号发起）的通知，`false` 表示只获取未被过滤的通知 (bool)
- **返回**: 包含以下字段的字典：
    - `requests`: 好友请求列表 (List[FriendRequest])

### `reject_friend_request(initiator_uid: str, is_filtered: bool = False, reason: str = None)`
拒绝好友请求
- **参数**:
    - `initiator_uid`: 请求发起者 UID (str)
    - `is_filtered`: 是否是被过滤的请求 (bool)
    - `reason`: 拒绝理由 (str)
- **返回**: 空字典。

### `send_friend_nudge(user_id: int, is_self: bool = False)`
发送好友戳一戳
- **参数**:
    - `user_id`: 好友 QQ 号 (int)
    - `is_self`: 是否戳自己 (bool)
- **返回**: 空字典。

### `send_profile_like(user_id: int, count: int = 1)`
发送名片点赞
- **参数**:
    - `user_id`: 好友 QQ 号 (int)
    - `count`: 点赞数量 (int)
- **返回**: 空字典。

---

## 文件 API

### `create_group_folder(group_id: int, folder_name: str)`
创建群文件夹
- **参数**:
    - `group_id`: 群号 (int)
    - `folder_name`: 文件夹名称 (str)
- **返回**: 包含以下字段的字典：
    - `folder_id`: 文件夹 ID (str)

### `delete_group_file(group_id: int, file_id: str)`
删除群文件
- **参数**:
    - `group_id`: 群号 (int)
    - `file_id`: 文件 ID (str)
- **返回**: 空字典。

### `delete_group_folder(group_id: int, folder_id: str)`
删除群文件夹
- **参数**:
    - `group_id`: 群号 (int)
    - `folder_id`: 文件夹 ID (str)
- **返回**: 空字典。

### `get_group_file_download_url(group_id: int, file_id: str)`
获取群文件下载链接
- **参数**:
    - `group_id`: 群号 (int)
    - `file_id`: 文件 ID (str)
- **返回**: 包含以下字段的字典：
    - `download_url`: 文件下载链接 (str)

### `get_group_files(group_id: int, parent_folder_id: str = "/")`
获取群文件列表
- **参数**:
    - `group_id`: 群号 (int)
    - `parent_folder_id`: 父文件夹 ID (str)
- **返回**: 包含以下字段的字典：
    - `files`: 文件列表 (List[GroupFileEntity])
    - `folders`: 文件夹列表 (List[GroupFolderEntity])

### `get_private_file_download_url(user_id: int, file_id: str, file_hash: str)`
获取私聊文件下载链接
- **参数**:
    - `user_id`: 好友 QQ 号 (int)
    - `file_id`: 文件 ID (str)
    - `file_hash`: 文件的 TriSHA1 哈希值 (str)
- **返回**: 包含以下字段的字典：
    - `download_url`: 文件下载链接 (str)

### `move_group_file(group_id: int, file_id: str, parent_folder_id: str = "/", target_folder_id: str = "/")`
移动群文件
- **参数**:
    - `group_id`: 群号 (int)
    - `file_id`: 文件 ID (str)
    - `parent_folder_id`: 文件所在的文件夹 ID (str)
    - `target_folder_id`: 目标文件夹 ID (str)
- **返回**: 空字典。

### `rename_group_file(group_id: int, file_id: str, new_file_name: str, parent_folder_id: str = "/")`
重命名群文件
- **参数**:
    - `group_id`: 群号 (int)
    - `file_id`: 文件 ID (str)
    - `new_file_name`: 新文件名称 (str)
    - `parent_folder_id`: 文件所在的文件夹 ID (str)
- **返回**: 空字典。

### `rename_group_folder(group_id: int, folder_id: str, new_folder_name: str)`
重命名群文件夹
- **参数**:
    - `group_id`: 群号 (int)
    - `folder_id`: 文件夹 ID (str)
    - `new_folder_name`: 新文件夹名 (str)
- **返回**: 空字典。

### `upload_group_file(group_id: int, file_uri: str, file_name: str, parent_folder_id: str = "/")`
上传群文件
- **参数**:
    - `group_id`: 群号 (int)
    - `file_uri`: 文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式 (str)
    - `file_name`: 文件名称 (str)
    - `parent_folder_id`: 目标文件夹 ID (str)
- **返回**: 包含以下字段的字典：
    - `file_id`: 文件 ID (str)

### `upload_private_file(user_id: int, file_uri: str, file_name: str)`
上传私聊文件
- **参数**:
    - `user_id`: 好友 QQ 号 (int)
    - `file_uri`: 文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式 (str)
    - `file_name`: 文件名称 (str)
- **返回**: 包含以下字段的字典：
    - `file_id`: 文件 ID (str)

---

## 消息 API

### `get_forwarded_messages(forward_id: str)`
获取合并转发消息内容
- **参数**:
    - `forward_id`: 转发消息 ID (str)
- **返回**: 包含以下字段的字典：
    - `messages`: 转发消息内容 (List[IncomingForwardedMessage])

### `get_history_messages(message_scene: str, peer_id: int, start_message_seq: int = None, limit: int = 20)`
获取历史消息列表
- **参数**:
    - `message_scene`: 消息场景 ("friend" | "group" | "temp") (str)
    - `peer_id`: 好友 QQ 号或群号 (int)
    - `start_message_seq`: 起始消息序列号，由此开始从新到旧查询，不提供则从最新消息开始 (int)
    - `limit`: 期望获取到的消息数量，最多 30 条 (int)
- **返回**: 包含以下字段的字典：
    - `messages`: 获取到的消息（message_seq 升序排列），部分消息可能不存在，如撤回的消息 (List[IncomingMessage])
    - `next_message_seq`: 下一页起始消息序列号 (int)

### `get_message(message_scene: str, peer_id: int, message_seq: int)`
获取消息
- **参数**:
    - `message_scene`: 消息场景 ("friend" | "group" | "temp") (str)
    - `peer_id`: 好友 QQ 号或群号 (int)
    - `message_seq`: 消息序列号 (int)
- **返回**: 包含以下字段的字典：
    - `message`: 消息内容 (IncomingMessage)

### `get_resource_temp_url(resource_id: str)`
获取临时资源链接
- **参数**:
    - `resource_id`: 资源 ID (str)
- **返回**: 包含以下字段的字典：
    - `url`: 临时资源链接 (str)

### `mark_message_as_read(message_scene: str, peer_id: int, message_seq: int)`
标记消息为已读
- **参数**:
    - `message_scene`: 消息场景 ("friend" | "group" | "temp") (str)
    - `peer_id`: 好友 QQ 号或群号 (int)
    - `message_seq`: 标为已读的消息序列号，该消息及更早的消息将被标记为已读 (int)
- **返回**: 空字典。

### `recall_group_message(group_id: int, message_seq: int)`
撤回群聊消息
- **参数**:
    - `group_id`: 群号 (int)
    - `message_seq`: 消息序列号 (int)
- **返回**: 空字典。

### `recall_private_message(user_id: int, message_seq: int)`
撤回私聊消息
- **参数**:
    - `user_id`: 好友 QQ 号 (int)
    - `message_seq`: 消息序列号 (int)
- **返回**: 空字典。

### `send_group_message(group_id: int, message: Union[str, List[dict]])`
发送群聊消息
- **参数**:
    - `group_id`: 群号 (int)
    - `message`: 消息内容 (Union[str, List[dict]])
- **返回**: 包含以下字段的字典：
    - `message_seq`: 消息序列号 (int)
    - `time`: 消息发送时间 (int)

### `send_private_message(user_id: int, message: Union[str, List[dict]])`
发送私聊消息
- **参数**:
    - `user_id`: 好友 QQ 号 (int)
    - `message`: 消息内容 (Union[str, List[dict]])
- **返回**: 包含以下字段的字典：
    - `message_seq`: 消息序列号 (int)
    - `time`: 消息发送时间 (int)

---

## 系统 API

### `get_cookies(domain: str)`
获取 Cookies
- **参数**:
    - `domain`: 需要获取 Cookies 的域名 (str)
- **返回**: 包含以下字段的字典：
    - `cookies`: 域名对应的 Cookies 字符串 (str)

### `get_csrf_token()`
获取 CSRF Token
- **返回**: 包含以下字段的字典：
    - `csrf_token`: CSRF Token (str)

### `get_friend_info(user_id: int, no_cache: bool = False)`
获取好友信息
- **参数**:
    - `user_id`: 好友 QQ 号 (int)
    - `no_cache`: 是否强制不使用缓存 (bool)
- **返回**: 包含以下字段的字典：
    - `friend`: 好友信息 (FriendEntity)

### `get_friend_list(no_cache: bool = False)`
获取好友列表
- **参数**:
    - `no_cache`: 是否强制不使用缓存 (bool)
- **返回**: 包含以下字段的字典：
    - `friends`: 好友列表 (List[FriendEntity])

### `get_group_info(group_id: int, no_cache: bool = False)`
获取群信息
- **参数**:
    - `group_id`: 群号 (int)
    - `no_cache`: 是否强制不使用缓存 (bool)
- **返回**: 包含以下字段的字典：
    - `group`: 群信息 (GroupEntity)

### `get_group_list(no_cache: bool = False)`
获取群列表
- **参数**:
    - `no_cache`: 是否强制不使用缓存 (bool)
- **返回**: 包含以下字段的字典：
    - `groups`: 群列表 (List[GroupEntity])

### `get_group_member_info(group_id: int, user_id: int, no_cache: bool = False)`
获取群成员信息
- **参数**:
    - `group_id`: 群号 (int)
    - `user_id`: 群成员 QQ 号 (int)
    - `no_cache`: 是否强制不使用缓存 (bool)
- **返回**: 包含以下字段的字典：
    - `member`: 群成员信息 (GroupMemberEntity)

### `get_group_member_list(group_id: int, no_cache: bool = False)`
获取群成员列表
- **参数**:
    - `group_id`: 群号 (int)
    - `no_cache`: 是否强制不使用缓存 (bool)
- **返回**: 包含以下字段的字典：
    - `members`: 群成员列表 (List[GroupMemberEntity])

### `get_impl_info()`
获取协议端信息
- **返回**: 包含以下字段的字典：
    - `impl_name`: 协议端名称 (str)
    - `impl_version`: 协议端版本 (str)
    - `qq_protocol_version`: 协议端使用的 QQ 协议版本 (str)
    - `qq_protocol_type`: 协议端使用的 QQ 协议平台 (str)
    - `milky_version`: 协议端实现的 Milky 协议版本，目前为 "1.0" (str)

### `get_login_info()`
获取登录信息
- **返回**: 包含以下字段的字典：
    - `uin`: 登录 QQ 号 (int)
    - `nickname`: 登录昵称 (str)

### `get_user_profile(user_id: int)`
获取用户个人信息
- **参数**:
    - `user_id`: 用户 QQ 号 (int)
- **返回**: 包含以下字段的字典：
    - `nickname`: 昵称 (str)
    - `qid`: QID (str)
    - `age`: 年龄 (int)
    - `sex`: 性别 (str)
    - `remark`: 备注 (str)
    - `bio`: 个性签名 (str)
    - `level`: QQ 等级 (int)
    - `country`: 国家或地区 (str)
    - `city`: 城市 (str)
    - `school`: 学校 (str)

---

## 群聊 API

### `accept_group_invitation(group_id: int, invitation_seq: int)`
同意他人邀请自身入群
- **参数**:
    - `group_id`: 群号 (int)
    - `invitation_seq`: 邀请序列号 (int)
- **返回**: 空字典。

### `accept_group_request(notification_seq: int, notification_type: str, group_id: int, is_filtered: bool = False)`
同意入群/邀请他人入群请求
- **参数**:
    - `notification_seq`: 请求对应的通知序列号 (int)
    - `notification_type`: 请求对应的通知类型 ("join_request" | "invited_join_request") (str)
    - `group_id`: 请求所在的群号 (int)
    - `is_filtered`: 是否是被过滤的请求 (bool)
- **返回**: 空字典。

### `delete_group_announcement(group_id: int, announcement_id: str)`
删除群公告
- **参数**:
    - `group_id`: 群号 (int)
    - `announcement_id`: 公告 ID (str)
- **返回**: 空字典。

### `get_group_announcements(group_id: int)`
获取群公告列表
- **参数**:
    - `group_id`: 群号 (int)
- **返回**: 包含以下字段的字典：
    - `announcements`: 群公告列表 (List[GroupAnnouncementEntity])

### `get_group_essence_messages(group_id: int, page_index: int, page_size: int)`
获取群精华消息列表
- **参数**:
    - `group_id`: 群号 (int)
    - `page_index`: 页码索引，从 0 开始 (int)
    - `page_size`: 每页包含的精华消息数量 (int)
- **返回**: 包含以下字段的字典：
    - `messages`: 精华消息列表 (List[GroupEssenceMessage])
    - `is_end`: 是否已到最后一页 (bool)

### `get_group_notifications(start_notification_seq: int = None, is_filtered: bool = False, limit: int = 20)`
获取群通知列表
- **参数**:
    - `start_notification_seq`: 起始通知序列号 (int)
    - `is_filtered`: `true` 表示只获取被过滤（由风险账号发起）的通知，`false` 表示只获取未被过滤的通知 (bool)
    - `limit`: 获取的最大通知数量 (int)
- **返回**: 包含以下字段的字典：
    - `notifications`: 获取到的群通知（notification_seq 降序排列），序列号不一定连续 (List[GroupNotification])
    - `next_notification_seq`: 下一页起始通知序列号 (int)

### `kick_group_member(group_id: int, user_id: int, reject_add_request: bool = False)`
踢出群成员
- **参数**:
    - `group_id`: 群号 (int)
    - `user_id`: 被踢的 QQ 号 (int)
    - `reject_add_request`: 是否拒绝加群申请，`false` 表示不拒绝 (bool)
- **返回**: 空字典。

### `quit_group(group_id: int)`
退出群
- **参数**:
    - `group_id`: 群号 (int)
- **返回**: 空字典。

### `reject_group_invitation(group_id: int, invitation_seq: int)`
拒绝他人邀请自身入群
- **参数**:
    - `group_id`: 群号 (int)
    - `invitation_seq`: 邀请序列号 (int)
- **返回**: 空字典。

### `reject_group_request(notification_seq: int, notification_type: str, group_id: int, is_filtered: bool = False, reason: str = None)`
拒绝入群/邀请他人入群请求
- **参数**:
    - `notification_seq`: 请求对应的通知序列号 (int)
    - `notification_type`: 请求对应的通知类型 ("join_request" | "invited_join_request") (str)
    - `group_id`: 请求所在的群号 (int)
    - `is_filtered`: 是否是被过滤的请求 (bool)
    - `reason`: 拒绝理由 (str)
- **返回**: 空字典。

### `send_group_announcement(group_id: int, content: str, image_uri: str = None)`
发送群公告
- **参数**:
    - `group_id`: 群号 (int)
    - `content`: 公告内容 (str)
    - `image_uri`: 公告附带图像文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式 (str)
- **返回**: 空字典。

### `send_group_message_reaction(group_id: int, message_seq: int, reaction: str, is_add: bool = True)`
发送群消息表情回应
- **参数**:
    - `group_id`: 群号 (int)
    - `message_seq`: 要回应的消息序列号 (int)
    - `reaction`: 表情 ID (str)
    - `is_add`: 是否添加表情，`false` 表示取消 (bool)
- **返回**: 空字典。

### `send_group_nudge(group_id: int, user_id: int)`
发送群戳一戳
- **参数**:
    - `group_id`: 群号 (int)
    - `user_id`: 被戳的群成员 QQ 号 (int)
- **返回**: 空字典。

### `set_group_avatar(group_id: int, image_uri: str)`
设置群头像
- **参数**:
    - `group_id`: 群号 (int)
    - `image_uri`: 头像文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式 (str)
- **返回**: 空字典。

### `set_group_essence_message(group_id: int, message_seq: int, is_set: bool = True)`
设置群精华消息
- **参数**:
    - `group_id`: 群号 (int)
    - `message_seq`: 消息序列号 (int)
    - `is_set`: 是否设置为精华消息，`false` 表示取消精华 (bool)
- **返回**: 空字典。

### `set_group_member_admin(group_id: int, user_id: int, is_set: bool = True)`
设置群管理员
- **参数**:
    - `group_id`: 群号 (int)
    - `user_id`: 被设置的 QQ 号 (int)
    - `is_set`: 是否设置为管理员，`false` 表示取消管理员 (bool)
- **返回**: 空字典。

### `set_group_member_card(group_id: int, user_id: int, card: str)`
设置群名片
- **参数**:
    - `group_id`: 群号 (int)
    - `user_id`: 被设置的群成员 QQ 号 (int)
    - `card`: 新群名片 (str)
- **返回**: 空字典。

### `set_group_member_mute(group_id: int, user_id: int, duration: int = 0)`
设置群成员禁言
- **参数**:
    - `group_id`: 群号 (int)
    - `user_id`: 被设置的 QQ 号 (int)
    - `duration`: 禁言持续时间（秒），设为 `0` 为取消禁言 (int)
- **返回**: 空字典。

### `set_group_member_special_title(group_id: int, user_id: int, special_title: str)`
设置群成员专属头衔
- **参数**:
    - `group_id`: 群号 (int)
    - `user_id`: 被设置的群成员 QQ 号 (int)
    - `special_title`: 新专属头衔 (str)
- **返回**: 空字典。

### `set_group_name(group_id: int, new_group_name: str)`
设置群名称
- **参数**:
    - `group_id`: 群号 (int)
    - `new_group_name`: 新群名称 (str)
- **返回**: 空字典。

### `set_group_whole_mute(group_id: int, is_mute: bool = True)`
设置群全员禁言
- **参数**:
    - `group_id`: 群号 (int)
    - `is_mute`: 是否开启全员禁言，`false` 表示取消全员禁言 (bool)
- **返回**: 空字典。

---


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
