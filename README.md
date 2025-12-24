# MilkyPy

MilkyPy 是一个为 [Milky 协议](https://milky.ntqqrev.org/) 开发的轻量级异步 Python SDK。

## 安装

目前可以通过 GitHub 直接安装：

```bash
pip install git+https://github.com/xiaoyu19960507/milkypy.git
```

## 完整示例

这是一个完整的机器人示例，包含了初始化、消息处理和运行逻辑：

```python
import asyncio
from milkypy import MilkyClient, Message, Text, Reply

# 1. 初始化客户端
# host: Milky 协议端运行的 IP
# port: 默认端口号（默认为 3010）
bot = MilkyClient(host="127.0.0.1", port=3010)

# 2. 监听并处理消息
@bot.on("message_receive")
async def handle_message(self, event: dict, self_id: int, time: int):
    # 提取纯文本内容
    content = Message.extract_text(event["segments"])
    
    peer_id = event["peer_id"]
    message_scene = event["message_scene"]
    message_seq = event["message_seq"]
    
    print(f"机器人 {self_id} 在 {time} 收到来自 {message_scene} {peer_id} 的消息: {content}")
    
    if "你好" in content:
        # 构造并发送回复消息
        msg = [
            Reply(message_seq),
            Text("你好！我是 MilkyPy 机器人。")
        ]
        
        if message_scene == "group":
            await self.send_group_message(peer_id, msg)
        else:
            await self.send_private_message(peer_id, msg)

# 3. 运行机器人
async def main():
    try:
        print("机器人启动中...")
        await bot.run()
    except KeyboardInterrupt:
        print("机器人已停止。")

if __name__ == "__main__":
    asyncio.run(main())
```

## 更多文档

详细的 API、事件和数据结构说明请参考 [docs](./docs/) 目录。

- [API 参考指南](./docs/api.md)
- [事件参考指南](./docs/events.md)
- [数据结构参考](./docs/structs.md)

## 许可证

本项目采用 MIT 许可证。
