from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory

from app.agent.model.qwen import llm_qwen
from app.agent.prompts.multi_chat_prompts import multi_chat_prompt

# 构建 LCEL
chain = multi_chat_prompt | llm_qwen | StrOutputParser()

# 实例化 chat_history
chat_history = ChatMessageHistory(messages=[HumanMessage("我叫 Cain")])
# 注入初始 history
# chat_history.add_user_message(HumanMessage(content="我们要做什么项目？"))
# chat_history.add_ai_message(AIMessage(content="我们要做编程智能体项目"))

for chunk in chain.stream({"question": "我叫什么？", "chat_history": chat_history.messages}):
    print(chunk, end="")