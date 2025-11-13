import uuid

# from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory, RunnableConfig
from langchain_community.agent_toolkits.file_management import FileManagementToolkit

from app.code_agent.model.qwen import llm_qwen
from app.code_agent.prompts.multi_chat_prompts import multi_chat_prompt


def get_session_history(session_id: str):
    return FileChatMessageHistory(f"{session_id}.json")

file_toolkit = FileManagementToolkit(root_dir='/Users/chenhui/Downloads/agent/llm/.temp')
file_tools = file_toolkit.get_tools()

llm_with_tools = llm_qwen.bind_tools(tools=file_tools)

# 构建 LCEL
chain = multi_chat_prompt | llm_with_tools | StrOutputParser()

# runnable: langchain 当中一切可以运行的对象
chain_with_history = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history",
)


# 构建多轮对话能力
def run_conversation():
    # 为用户创建一个 id
    session_id = uuid.uuid4()
    # session_id = 'e5a36d27-5826-4c17-9f8e-f90ac245f27c'
    # print(session_id)

    # 创建一个无限的死循环，维持一个对话
    while True:
        user_input = input("用户：")
        print(user_input)
        if user_input.lower() == "exit" or user_input.lower() == ":wq":
            break

        # 调用大模型
        response = chain_with_history.stream(
            {"question": user_input},
            config=RunnableConfig(
                configurable={
                    "session_id": session_id,
                }
            )
        )

        print("助理：", end="")

        for chunk in response:
            print(chunk, end="")

        print("\n")


if __name__ == "__main__":
    run_conversation()

# # 实例化 chat_history
# chat_history = ChatMessageHistory(messages=[HumanMessage("我叫 Cain")])
#
# for chunk in chain.stream({"question": "我叫什么？", "chat_history": chat_history.messages}):
#     print(chunk, end="")
