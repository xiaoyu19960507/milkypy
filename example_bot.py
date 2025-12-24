import os
from milkypy import MilkyClient, Text, Reply
import logging
from datetime import datetime
import asyncio
import traceback

# 从环境变量获取配置
HOST = os.environ.get('MILKY_HOST', '127.0.0.1')
API_PORT = os.environ.get('MILKY_API_PORT', '3010')
EVENT_PORT = os.environ.get('MILKY_EVENT_PORT', '3010')
TOKEN = os.environ.get('MILKY_TOKEN', None)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("milkypy")

# 初始化客户端
bot = MilkyClient(
    host=HOST, 
    api_port=int(API_PORT) if API_PORT else None, 
    event_port=int(EVENT_PORT) if EVENT_PORT else None, 
    token=TOKEN
)

# 监听消息事件
@bot.on("message_receive")
async def handle_message(self: MilkyClient, event: dict, self_id: int, time: int):
    """
    处理接收到的消息。
    """
    # 提取纯文本内容
    content = "".join([segment["data"]["text"] for segment in event["segments"] if segment["type"] == "text"])
    
    peer_id = event["peer_id"]
    message_scene = event["message_scene"]
    message_seq = event["message_seq"]
    
    time_str = datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"机器人 {self_id} 在 {time_str} 接收到的来自 {message_scene} {peer_id} 的消息: {content}")
    
    if "/你好" in content:
        # 构造并发送回复消息
        msg = [
            Reply(message_seq),
            Text("你好！我是 MilkyPy 机器人。")
        ]
        
        if message_scene == "group":
            await self.send_group_message(peer_id, msg)

# 监听戳一戳事件作为示例
@bot.on("group_nudge")
async def handle_nudge(self: MilkyClient, event: dict, self_id: int, time: int):
    """
    处理群戳一戳事件。
    """
    time_str = datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"机器人 {self_id} 在 {time_str} 收到事件: 群 {event['group_id']} 中 {event['sender_id']} 戳了 {event['receiver_id']}")


# 启动机器人
if __name__ == "__main__":
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("机器人已主动停止运行,再见！")
    except Exception as e:
        logger.critical(f"机器人运行过程中发生未捕获的致命错误: {e}")
        logger.error(traceback.format_exc())
    
