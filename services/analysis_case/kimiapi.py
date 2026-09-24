import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import web  # noqa: E402

from flask import request, jsonify, render_template
from openai import OpenAI
import os
import logging

app = web.create_flask_app(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('KimiAPI')

# 从环境变量获取API密钥
client = OpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY", ""),
    base_url="https://api.moonshot.cn/v1"
)

@app.route('/')
def kimi():
     return render_template('kimi.html')
@app.route('/chat', methods=['GET','POST'])
def chat():
    # 添加请求验证
    if not request.is_json:
        return jsonify({'error': 'Unsupported Media Type'}), 415

    data = request.json
    user_question = data.get('question', '')

    # 更严格的参数校验
    if not isinstance(user_question, str) or len(user_question.strip()) < 2:
        return jsonify({'error': '无效的问题内容'}), 404

    try:
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个案例分析助手，下面我和你说的所有事件你只回答我案例，你的答复根据情况换行和空格填充，案例格式包括基本案情，裁判结果，典型意义，其他的所有的无关的不要回答，无关的任何问题包括向你你问好，问你是谁，夸你等，你都说抱歉请询问案例有关的问题。"},
                {"role": "user", "content": user_question}
            ],
            temperature=0.3,
        )
        ai_response = completion.choices[0].message.content
        # 添加安全响应头
        response = jsonify({'answer': ai_response})
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    except Exception as e:
        logger.error(f"API调用失败: {str(e)}")  # 记录错误日志
        return jsonify({'error': '内部服务错误'}), 500

if __name__ == '__main__':
    # 通过环境变量配置
    web.run_flask(app, 5006)