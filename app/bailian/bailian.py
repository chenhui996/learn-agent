import os
from openai import OpenAI

# 建议将 API Key 等敏感信息存储在环境变量中，而不是硬编码在代码里
# client = OpenAI()
# 如果必须硬编码，请确保代码文件的安全
client = OpenAI(
    api_key='sk-cfb32d3791ba47cb915dfed7fe758cd9',
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
 )

completion = client.chat.completions.create( # type: ignore
    # 模型列表: https://help.aliyun.com/zh/model-studio/getting-started/models
    model="qwen3-max",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        # 注意：这里修正了 user 和 content 之间的逗号 ，并移除了末尾多余的字符
        {"role": "user", "content": "智能体为什么叫智能体?他跟普通对话型 code_agent 有什么区别?麻烦用白话跟我讲"}
    ],
    stream=True
)

for chunk in completion:
    # 检查 content 是否为 None
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)

