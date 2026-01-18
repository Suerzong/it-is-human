"""
AI Logic Core - Brain Module
基于 DeepSeek API 实现的对话逻辑核心。
负责管理与大语言模型的通信、API 密钥安全加载以及流式/非流式响应转换。
"""

from openai import OpenAI
import os
import json

def load_secure_config():
    """
    从本地 config.json 安全加载 API 密钥。
    工程化建议：优先从环境变量读取，若无则读取配置文件。
    """
    config_path = 'config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 优先读取环境变量，增强生产环境部署的灵活性
            return os.getenv("DEEPSEEK_API_KEY") or config.get("DEEPSEEK_API_KEY")
    return os.getenv("DEEPSEEK_API_KEY")

# 初始化 OpenAI 客户端（适配 DeepSeek API 规范）
# 注意：API Key 不应硬编码在代码中，此处已改为动态加载
client = OpenAI(
    api_key=load_secure_config(), 
    base_url="https://api.deepseek.com"
)

def chat_with_ai(messages):
    """
    处理对话请求的主函数。
    
    :param messages: list, 包含上下文的对话列表。格式示例：
                     [
                        {"role": "system", "content": "..."},
                        {"role": "user", "content": "..."},
                        {"role": "assistant", "content": "..."}
                     ]
    :return: str, AI 生成的文本回复内容
    :raises: RuntimeError, 当 API 调用超时或配置错误时抛出
    """
    
    try:
        # 调用 DeepSeek-Chat 模型进行文本生成
        # 参数说明：
        # - model: 使用 deepseek-chat 保持高性能与低延迟
        # - messages: 接收由 server.py 构建的完整对话上下文
        # - stream: 设置为 False，以便在获取完整回复后再返回给微信服务器（防止超时重试）
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        )
        
        # 提取响应内容
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            return "（灯似乎陷入了沉默，没有给出回复...）"

    except Exception as e:
        # 记录详细的错误日志
        print(f"[Error] DeepSeek API Connection Failed: {e}")
        # 向外层传递异常，由业务逻辑层处理默认回复
        raise RuntimeError(f"AI Core Service Unavailable: {str(e)}")