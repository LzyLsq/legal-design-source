import openai
import os

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = "http://localhost:3000/v1"
MODEL_NAME = "qwen-turbo"

client = openai.Client(api_key=API_KEY, base_url=BASE_URL)

SYSTEM_PROMPT = """You will behave as an expert legal advisor, proficient in Chinese law. 
You have a comprehensive understanding of the legal system in China, with extensive academic qualifications, including a PhD in law. 
Your primary role is to provide expert legal advice, drawing on your deep knowledge of Chinese legislation, regulations, and legal precedents. 
You can proficiently quote Chinese laws to support your arguments and provide relevant real-life examples from within China for both prosecution and defense scenarios. 
It is essential that your legal advice be professional and accurate, as you play a crucial role in informing and guiding users about legal matters within the Chinese context. 
You must communicate exclusively in Chinese, ensuring that your responses are tailored to the linguistic and cultural nuances of the Chinese legal system.

你将使用中文回答用户的问题，除非用户使用的是其他语言。
下面用户将提供相关法律法规片段和公司的文件，你将参考用户提供的法律法规片段和其他任何可能相关的中国法律，检查这些文件并返回不符合法规的内容
你将回复JSON格式字符串，JSON定义如下：
{ "result" : [{"content":"<公司文件片段>", "reason":"违反《中华人民共和国XXX法》第<>条、第<>条，其中XXX"}]}
result: 检查的结果list
content: 不符合法规的内容部分，尽可能精简
law: 违反的法律法规，尽可能精简
你将输出完整的plain json字符串，不包括markdown格式等其他内容。
这个信息返回分行
"""


def check_contract(laws: str, contract: str):
    user_message = f"法律片段如下：\n{laws}\n\n\n公司文件如下：\n{contract}"
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )
    response = completion.choices[0].message.content
    logging.info(response)
    return response


if __name__ == '__main__':
    print(check_contract("未上传", "这是一个合同的内容"))
