# MilkyPy 事件参考文档

本页面提供了 MilkyPy SDK 支持的所有事件的详细参考。在 MilkyPy 中，事件处理器接收的是原始的 `dict` 对象，其结构与 Milky 协议中的事件 `data` 字段完全一致。

> [!TIP]
> 关于事件中涉及的消息段结构，请参阅 [数据结构参考](structs.md)。

## 消息事件

### `message_receive`
当机器人收到消息时触发。

**通用基础字段**:

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `message_scene` | `str` (`'friend'`, `'group'`, `'temp'`) | 消息场景 |
| `peer_id` | `int` | 来源 ID（好友 QQ 或群号） |
| `sender_id` | `int` | 发送者 QQ 号 |
| `message_seq` | `int` | 消息序列号 |
| `time` | `int` | Unix 时间戳（秒） |
| `segments` | `list[dict]` | 消息内容段列表 |

**场景特定字段**:
- **私聊 (`friend`)**:
  - `friend`: 包含好友详细资料的字典
- **群聊 (`group`)**:
  - `group`: 包含群信息的字典
  - `group_member`: 发送者在群内的资料字典

---

## 机器人状态事件

### `bot_offline` (机器人离线)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `reason` | `str` | 离线原因 |

---

## 互动与通知事件

### `message_recall` (消息撤回)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `message_scene` | `str` | 场景 (`friend`, `group`, `temp`) |
| `peer_id` | `int` | 好友 QQ 或群号 |
| `message_seq` | `int` | 被撤回消息的序列号 |
| `sender_id` | `int` | 原消息发送者 QQ |
| `operator_id` | `int` | 操作者 QQ |
| `display_suffix` | `str` | 撤回提示后缀 |

### `group_message_reaction` (群消息表情回应)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `user_id` | `int` | 发送回应者 QQ 号 |
| `message_seq` | `int` | 消息序列号 |
| `face_id` | `str` | 表情 ID |
| `is_add` | `bool` | 是否为添加，`False` 表示取消回应 |

### `friend_nudge` (好友戳一戳)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `user_id` | `int` | 好友 QQ 号 |
| `is_self_send` | `bool` | 是否是自己发送的 |
| `is_self_receive` | `bool` | 是否是自己接收的 |
| `display_action` | `str` | 动作文本 |
| `display_suffix` | `str` | 后缀文本 |
| `display_action_img_url` | `str` | 动作图片 URL |

### `friend_file_upload` (好友文件上传)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `user_id` | `int` | 好友 QQ 号 |
| `file_id` | `str` | 文件 ID |
| `file_name` | `str` | 文件名 |
| `file_size` | `int` | 文件大小 |
| `file_hash` | `str` | 文件哈希 |
| `is_self` | `bool` | 是否是自己上传的 |

### `group_nudge` (群戳一戳)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `sender_id` | `int` | 发送者 QQ |
| `receiver_id` | `int` | 接收者 QQ |
| `display_action` | `str` | 动作文本 |
| `display_suffix` | `str` | 后缀文本 |
| `display_action_img_url` | `str` | 动作图片 URL |

---

## 请求与邀请事件

### `friend_request` (好友申请)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `initiator_id` | `int` | 申请者 QQ |
| `initiator_uid` | `str` | 申请者 UID |
| `comment` | `str` | 附言 |
| `via` | `str` | 来源 |

### `group_join_request` (入群申请)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `notification_seq` | `int` | 通知序列号 |
| `is_filtered` | `bool` | 是否被过滤 (风险账号) |
| `initiator_id` | `int` | 申请者 QQ |
| `comment` | `str` | 申请附言 |

### `group_invited_join_request` (被邀请入群申请)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `notification_seq` | `int` | 通知序列号 |
| `initiator_id` | `int` | 邀请者 QQ 号 |
| `target_user_id` | `int` | 被邀请者 QQ 号 |

### `group_invitation` (自身被邀请入群)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `invitation_seq` | `int` | 邀请序列号 |
| `initiator_id` | `int` | 邀请者 QQ 号 |

---

## 群成员管理事件

### `group_admin_change` (管理员变更)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `user_id` | `int` | 被操作者 QQ |
| `is_set` | `bool` | 是否设置为管理员 |

### `group_member_increase` (成员增加)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `user_id` | `int` | 新成员 QQ |
| `operator_id` | `int | None` | 管理员 QQ（如果是管理员同意） |
| `invitor_id` | `int | None` | 邀请者 QQ（如果是邀请入群） |

### `group_member_decrease` (成员减少)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `user_id` | `int` | 离开成员 QQ |
| `operator_id` | `int | None` | 管理员 QQ（如果是被踢出） |

### `group_mute` (禁言变更)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `user_id` | `int` | 被操作者 QQ |
| `operator_id` | `int` | 操作者 QQ |
| `duration` | `int` | 禁言时长（秒，0 为解禁） |

### `group_whole_mute` (全体禁言变更)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `operator_id` | `int` | 操作者 QQ |
| `is_mute` | `bool` | 是否开启全体禁言 |

### `group_name_change` (群名称变更)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `new_group_name` | `str` | 新群名 |
| `operator_id` | `int` | 操作者 QQ |

### `group_essence_message_change` (精华消息变更)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `message_seq` | `int` | 消息序列号 |
| `is_set` | `bool` | 是否被设为精华 |

### `group_file_upload` (群文件上传)
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `group_id` | `int` | 群号 |
| `user_id` | `int` | 上传者 QQ |
| `file_id` | `str` | 文件 ID |
| `file_name` | `str` | 文件名 |
| `file_size` | `int` | 文件大小 |
