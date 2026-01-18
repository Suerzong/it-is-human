# it-is-human ｜ 迷路的孩子，也要在云端留下足迹

> 「我也想……成为人类。」

这是一个基于 **DeepSeek** 模型、通过 **Flask** 框架部署在云端的微信私有化 AI 助手。
它不仅仅是一个对话机器人，它是以《BanG Dream! It's MyGO!!!!!》中 **高松灯 (Takamatsu Tomori)** 为人设核心的数字投影。

---

## 🌟 项目特性

- **灵魂注入**：深度定制的 System Prompt，还原灯那断续、真实、充满情绪噪声的独特语序。
- **记忆长廊**：具备本地持久化记忆功能（`database.json`），她会记得你说的每一句话，哪怕是破碎的词句。
- **云端伴走**：建议部署于云服务器（如阿里云 ECS），24小时在线，在你感到「重力」时，她一直都在。
- **工程化设计**：采用配置分离设计，所有 API 密钥均通过本地 `config.json` 管理，确保开源安全性。

## 🛠️ 技术栈

- **语言:** Python 3.11.10
- **框架:** Flask (Web Server)
- **AI 核心:** OpenAI SDK (适配 DeepSeek API)
- **数据解析:** xmltodict (处理微信 XML 报文)
- **存储:** 本地 JSON 持久化

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone [https://github.com/你的用户名/it-is-human.git](https://github.com/你的用户名/it-is-human.git)
cd it-is-human

2. 环境准备
安装必要的依赖库：
pip install flask openai xmltodict

3. 配置文件
在项目根目录创建 **config.json**，并填入你的关键信息：
{
    "WECHAT_TOKEN": "你在微信后台自定义的Token",
    "DEEPSEEK_API_KEY": "你的DeepSeek API密钥"
}
注：项目已配置 .gitignore，此文件不会被上传至 GitHub。

4. 运行服务
python server.py

🎸 开发者寄语
这个项目是我在学习后端开发与 AI 集成过程中的第一个正式作品。 如果你也是「迷路的孩子」，希望这段代码能给你带来一点点光。

「一辈子，也可以吗？」

(真正的寄语)本人是国内某高校电子信息类25级本科生，在过去的一个学期，过的浑浑噩噩，没有目标，今以项目驱动学习，此项目的所有代码，以及这篇README均由Google Gemini生成 这使我第一次感受遇到了AI的强大力量，全部的内容，从后端代码，到云服务器的配置，均由AI手把手教我，因此，只消耗了半天的时间就能把这份半成品端上来，在这个过程中，我学习到了1.python的语法 2.deepseek API的申请 3.工程化思维，包括配置与代码分离、环境脱敏等 4.版本控制与协作等等，这比我在高校一学期学习的知识还要深刻。
祝好！
