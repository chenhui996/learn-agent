from langchain_core.output_parsers import StrOutputParser

from app.agent.model.qwen import llm_qwen
from app.agent.prompts.multi_chat_prompts import multi_chat_prompt

# 构建 LCEL
chain = multi_chat_prompt | llm_qwen | StrOutputParser()

for chunk in chain.stream({"question": "你是谁？", "chat_history": []}):
    print(chunk, end="")