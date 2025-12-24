# MilkyPy 数据结构参考

本页面详细列出了 MilkyPy 中使用的核心数据结构、消息段及其 JSON 字段。所有的结构均为原始的 `dict`，你可以直接根据字段名进行访问。

---

## 核心实体 (Entities)

核心实体是 API 返回或事件推送中常见的复合 JSON 对象。

### `FriendCategoryEntity` (好友分组实体)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `category_id` | `int` | 好友分组 ID |
| `category_name` | `str` | 好友分组名称 |

### `FriendEntity` (好友实体)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `user_id` | `int` | 用户 QQ 号 |
| `nickname` | `str` | 用户昵称 |
| `sex` | `str` | 用户性别 (`male`, `female`, `unknown`) |
| `qid` | `str` | 用户 QID |
| `remark` | `str` | 好友备注 |
| `category` | `FriendCategoryEntity` | 好友分组 |

### `FriendRequest` (好友请求实体)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `time` | `int` | 请求发起时的 Unix 时间戳（秒） |
| `initiator_id` | `int` | 请求发起者 QQ 号 |
| `initiator_uid` | `str` | 请求发起者 UID |
| `target_user_id` | `int` | 目标用户 QQ 号 |
| `target_user_uid` | `str` | 目标用户 UID |
| `state` | `str` | 请求状态 (`pending`, `accepted`, `rejected`, `ignored`) |
| `comment` | `str` | 申请附加信息 |
| `via` | `str` | 申请来源 |
| `is_filtered` | `bool` | 请求是否被过滤（发起自风险账户） |

### `GroupAnnouncementEntity` (群公告实体)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `announcement_id` | `str` | 公告 ID |
| `user_id` | `int` | 发送者 QQ 号 |
| `time` | `int` | Unix 时间戳（秒） |
| `content` | `str` | 公告内容 |
| `image_url` | `str` | 公告图片 URL (可选) |

### `GroupEntity` (群实体)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `group_name` | `str` | 群名称 |
| `member_count` | `int` | 群成员数量 |
| `max_member_count` | `int` | 群容量 |

### `GroupEssenceMessage` (群精华消息)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `message_seq` | `int` | 消息序列号 |
| `message_time` | `int` | 消息发送时的 Unix 时间戳（秒） |
| `sender_id` | `int` | 发送者 QQ 号 |
| `sender_name` | `str` | 发送者名称 |
| `operator_id` | `int` | 设置精华的操作者 QQ 号 |
| `operator_name` | `str` | 设置精华的操作者名称 |
| `operation_time` | `int` | 消息被设置精华时的 Unix 时间戳（秒） |
| `segments` | `List[IncomingSegment]` | 消息段列表 |

### `GroupFileEntity` (群文件实体)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `file_id` | `str` | 文件 ID |
| `file_name` | `str` | 文件名称 |
| `parent_folder_id` | `str` | 父文件夹 ID |
| `file_size` | `int` | 文件大小（字节） |
| `uploaded_time` | `int` | 上传时的 Unix 时间戳（秒） |
| `expire_time` | `int` | 过期时的 Unix 时间戳（秒） (可选) |
| `uploader_id` | `int` | 上传者 QQ 号 |
| `downloaded_times` | `int` | 下载次数 |

### `GroupFolderEntity` (群文件夹实体)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `folder_id` | `str` | 文件夹 ID |
| `parent_folder_id` | `str` | 父文件夹 ID |
| `folder_name` | `str` | 文件夹名称 |
| `created_time` | `int` | 创建时的 Unix 时间戳（秒） |
| `last_modified_time` | `int` | 最后修改时的 Unix 时间戳（秒） |
| `creator_id` | `int` | 创建者 QQ 号 |
| `file_count` | `int` | 文件数量 |

### `GroupMemberEntity` (群成员实体)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `user_id` | `int` | 用户 QQ 号 |
| `nickname` | `str` | 用户昵称 |
| `sex` | `str` | 用户性别 (`male`, `female`, `unknown`) |
| `group_id` | `int` | 群号 |
| `card` | `str` | 成员备注 |
| `title` | `str` | 专属头衔 |
| `level` | `int` | 群等级，注意和 QQ 等级区分 |
| `role` | `str` | 权限等级 (`owner`, `admin`, `member`) |
| `join_time` | `int` | 入群时间，Unix 时间戳（秒） |
| `last_sent_time` | `int` | 最后发言时间，Unix 时间戳（秒） |
| `shut_up_end_time` | `int` | 禁言结束时间，Unix 时间戳（秒） (可选) |

### `GroupNotification` (群通知实体)
这是一个联合类型。所有类型均包含以下基础字段：
- `group_id`: 群号 (int)
- `notification_seq`: 通知序列号 (int)
- `type`: 类型标识 (`join_request`, `admin_change`, `kick`, `quit`, `invited_join_request`)

包含以下变体：

#### `join_request` (用户入群请求)
- `is_filtered`: 请求是否被过滤（发起自风险账户） (bool)
- `initiator_id`: 发起者 QQ 号 (int)
- `state`: 请求状态 (`pending`, `accepted`, `rejected`, `ignored`) (str)
- `operator_id`: 处理请求的管理员 QQ 号 (可选) (int)
- `comment`: 入群请求附加信息 (str)

#### `admin_change` (群管理员变更通知)
- `target_user_id`: 被设置/取消用户 QQ 号 (int)
- `is_set`: 是否被设置为管理员，`false` 表示被取消管理员 (bool)
- `operator_id`: 操作者（群主）QQ 号 (int)

#### `kick` (群成员被移除通知)
- `target_user_id`: 被移除用户 QQ 号 (int)
- `operator_id`: 移除用户的管理员 QQ 号 (int)

#### `quit` (群成员退群通知)
- `target_user_id`: 退群用户 QQ 号 (int)

#### `invited_join_request` (群成员邀请他人入群请求)
- `initiator_id`: 邀请者 QQ 号 (int)
- `target_user_id`: 被邀请用户 QQ 号 (int)
- `state`: 请求状态 (`pending`, `accepted`, `rejected`, `ignored`) (str)
- `operator_id`: 处理请求的管理员 QQ 号 (可选) (int)

---

## 消息结构 (Message Structures)

### `IncomingForwardedMessage` (接收转发消息)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `sender_name` | `str` | 发送者名称 |
| `avatar_url` | `str` | 发送者头像 URL |
| `time` | `int` | 消息 Unix 时间戳（秒） |
| `segments` | `List[IncomingSegment]` | 消息段列表 |

### `IncomingMessage` (接收消息)
这是一个联合类型。所有类型均包含以下基础字段：
- `message_seq`: 消息序列号 (int)
- `peer_id`: 好友 QQ 号或群号 (int)
- `segments`: 消息段列表 (List[IncomingSegment])
- `sender_id`: 发送者 QQ 号 (int)
- `time`: 消息 Unix 时间戳（秒） (int)
- `message_scene`: 类型标识 (`friend`, `group`, `temp`)

包含以下变体：

#### `friend` (好友消息)
- `friend`: 好友信息 (FriendEntity)

#### `group` (群消息)
- `group`: 群信息 (GroupEntity)
- `group_member`: 群成员信息 (GroupMemberEntity)

#### `temp` (临时会话消息)
- `group`: 临时会话发送者的所在的群信息 (可选) (GroupEntity)

### `OutgoingForwardedMessage` (发送转发消息)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `user_id` | `int` | 发送者 QQ 号 |
| `sender_name` | `str` | 发送者名称 |
| `segments` | `List[OutgoingSegment]` | 消息段列表 |

---

## 消息段 (Message Segments)

### `IncomingSegment` (接收消息段)
这是一个联合类型。所有类型均包含以下基础字段：
- `type`: 类型标识 (`text`, `mention`, `mention_all`, `face`, `reply`, `image`, `record`, `video`, `file`, `forward`, `market_face`, `light_app`, `xml`)

包含以下变体：

#### `text` (文本消息段)
- **data**: `{"text": str}`
    - `text`: 文本内容

#### `mention` (提及消息段)
- **data**: `{"user_id": int}`
    - `user_id`: 提及的 QQ 号

#### `mention_all` (提及全体消息段)
- `data`: 提及全体消息段 (dict)

#### `face` (表情消息段)
- **data**: `{"face_id": str}`
    - `face_id`: 表情 ID

#### `reply` (回复消息段)
- **data**: `{"message_seq": int}`
    - `message_seq`: 被引用的消息序列号

#### `image` (图片消息段)
- **data**: `{"resource_id": str, "temp_url": str, "width": int, "height": int, "summary": str, "sub_type": str}`
    - `resource_id`: 资源 ID
    - `temp_url`: 临时 URL
    - `width`: 图片宽度
    - `height`: 图片高度
    - `summary`: 图片预览文本
    - `sub_type`: 图片类型 (`normal`, `sticker`)

#### `record` (语音消息段)
- **data**: `{"resource_id": str, "temp_url": str, "duration": int}`
    - `resource_id`: 资源 ID
    - `temp_url`: 临时 URL
    - `duration`: 语音时长（秒）

#### `video` (视频消息段)
- **data**: `{"resource_id": str, "temp_url": str, "width": int, "height": int, "duration": int}`
    - `resource_id`: 资源 ID
    - `temp_url`: 临时 URL
    - `width`: 视频宽度
    - `height`: 视频高度
    - `duration`: 视频时长（秒）

#### `file` (文件消息段)
- **data**: `{"file_id": str, "file_name": str, "file_size": int, "file_hash": str}`
    - `file_id`: 文件 ID
    - `file_name`: 文件名称
    - `file_size`: 文件大小（字节）
    - `file_hash`: 文件的 TriSHA1 哈希值，仅在私聊文件中存在 (可选)

#### `forward` (合并转发消息段)
- **data**: `{"forward_id": str}`
    - `forward_id`: 合并转发 ID

#### `market_face` (市场表情消息段)
- **data**: `{"url": str}`
    - `url`: 市场表情 URL

#### `light_app` (小程序消息段)
- **data**: `{"app_name": str, "json_payload": str}`
    - `app_name`: 小程序名称
    - `json_payload`: 小程序 JSON 数据

#### `xml` (XML 消息段)
- **data**: `{"service_id": int, "xml_payload": str}`
    - `service_id`: 服务 ID
    - `xml_payload`: XML 数据

### `OutgoingSegment` (发送消息段)
这是一个联合类型。所有类型均包含以下基础字段：
- `type`: 类型标识 (`text`, `mention`, `mention_all`, `face`, `reply`, `image`, `record`, `video`, `forward`)

包含以下变体：

#### `text` (文本消息段)
- **data**: `{"text": str}`
    - `text`: 文本内容

#### `mention` (提及消息段)
- **data**: `{"user_id": int}`
    - `user_id`: 提及的 QQ 号

#### `mention_all` (提及全体消息段)
- `data`: 提及全体消息段 (dict)

#### `face` (表情消息段)
- **data**: `{"face_id": str}`
    - `face_id`: 表情 ID

#### `reply` (回复消息段)
- **data**: `{"message_seq": int}`
    - `message_seq`: 被引用的消息序列号

#### `image` (图片消息段)
- **data**: `{"uri": str, "summary": str, "sub_type": str}`
    - `uri`: 文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式
    - `summary`: 图片预览文本 (可选)
    - `sub_type`: 图片类型 (`normal`, `sticker`)

#### `record` (语音消息段)
- **data**: `{"uri": str}`
    - `uri`: 文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式

#### `video` (视频消息段)
- **data**: `{"uri": str, "thumb_uri": str}`
    - `uri`: 文件 URI，支持 `file://` `http(s)://` `base64://` 三种格式
    - `thumb_uri`: 封面图片 URI (可选)

#### `forward` (合并转发消息段)
- **data**: `{"messages": List[OutgoingForwardedMessage]}`
    - `messages`: 合并转发消息段
