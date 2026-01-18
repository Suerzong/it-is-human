"""
WeChat AI Assistant Server
基于 Flask 框架实现的微信公众号后端服务，集成 DeepSeek AI 实现长文本对话与上下文记忆。
"""

from flask import Flask, request
import hashlib
import xmltodict
import time
import json
import os
from brain import chat_with_ai 

app = Flask(__name__)

# --- 全局配置与持久化存储变量 ---
DB_FILE = 'database.json'  # 本地轻量级 JSON 数据库，用于存储用户历史对话上下文

def load_config():
    """
    从本地加载敏感配置文件。
    采用配置与代码分离原则，避免 TOKEN 和 API_KEY 泄露至开源仓库。
    :return: 包含配置信息的字典
    """
    config_path = 'config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # 异常处理：提示开发者创建必要的本地配置文件
        raise FileNotFoundError("Critical Error: 'config.json' missing. Please create it based on the template.")

# 初始化加载全局配置
config = load_config()
TOKEN = config.get("WECHAT_TOKEN")

def load_memories():
    """
    初始化加载历史记忆。
    从 JSON 文件读取用户对话历史，若文件损坏或不存在则返回空字典。
    """
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Database Read Error: {e}")
            return {}
    return {}

def save_memories(memories):
    """
    将当前会话记忆持久化到本地文件。
    :param memories: 包含所有用户对话上下文的字典
    """
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            # ensure_ascii=False 确保中文内容不被转码，indent=4 提升文件可读性
            json.dump(memories, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Database Write Error: {e}")

# 程序启动时同步加载内存映射
user_memories = load_memories()

@app.route("/wechat", methods=["GET", "POST"])
def wechat_handler():
    """
    微信公众号入口路由。
    处理微信平台的身份验证(GET)以及用户消息分发(POST)。
    """
    
    # 场景一：微信服务器发起的服务器有效性校验 (GET)
    if request.method == "GET":
        signature = request.args.get('signature') # 微信加密签名
        timestamp = request.args.get('timestamp') # 时间戳
        nonce = request.args.get('nonce')         # 随机数
        echostr = request.args.get('echostr')     # 验证成功后需返回的随机字符串
        
        if not all([signature, timestamp, nonce]):
            return "Invalid access attempt."

        # 按照微信官方文档的 SHA1 校验逻辑进行身份验证
        data = [TOKEN, timestamp, nonce]
        data.sort() # 字典序排序
        sha1 = hashlib.sha1()
        sha1.update(''.join(data).encode('utf-8'))
        hashcode = sha1.hexdigest()
        
        # 对比本地计算的签名与微信传来的签名是否一致
        if hashcode == signature:
            return echostr
        else:
            return "Signcheck failed."

    # 场景二：处理用户发送的消息请求 (POST)
    if request.method == "POST":
        xml_data = request.data
        # 将微信发送的 XML 数据解析为 Python 字典以便操作
        msg_dict = xmltodict.parse(xml_data).get('xml')
        user_id = msg_dict.get('FromUserName')   # 发送者的 OpenID
        my_id = msg_dict.get('ToUserName')       # 公众号微信号
        msg_type = msg_dict.get('MsgType')       # 消息类型（如 text, image 等）

        if msg_type == 'text':
            user_text = msg_dict.get('Content')
            print(f"[Log] Received from {user_id}: {user_text}")

            # 构建对话 Payload，包含 System Prompt 和历史 Context
            messages = [
                {"role": "system", "content": "你叫高松燈...（此处建议在开源版本中使用变量引用人设）"}
            ]
            
            # 策略：滑动窗口提取最近 5 轮对话，平衡上下文关联度与 Token 消耗
            history = user_memories.get(user_id, [])[-5:]
            for item in history:
                messages.append({"role": "user", "content": item["user"]})
                messages.append({"role": "assistant", "content": item["ai"]})
            
            # 追加当前用户输入
            messages.append({"role": "user", "content": user_text})

            try:
                # 调用 AI 引擎模块获取回复内容
                reply_content = chat_with_ai(messages)
                
                # 实时更新该用户的内存记录并持久化
                if user_id not in user_memories:
                    user_memories[user_id] = []
                user_memories[user_id].append({"user": user_text, "ai": reply_content})
                save_memories(user_memories)

            except Exception as e:
                print(f"AI Engine Error: {e}")
                reply_content = "（系统正在努力处理中，请稍后再试...）"

            # 按照微信官方 XML 格式要求构造返回包
            reply_xml = f"""
            <xml>
                <ToUserName><![CDATA[{user_id}]]></ToUserName>
                <FromUserName><![CDATA[{my_id}]]></FromUserName>
                <CreateTime>{int(time.time())}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{reply_content}]]></Content>
            </xml>
            """
            return reply_xml
        
        # 对于非文本消息，默认返回 success（微信要求）
        return "success"

if __name__ == "__main__":
    # 生产环境运行配置：监听全网段，使用 80 端口（公众号默认请求端口）
    app.run(host='0.0.0.0', port=80)