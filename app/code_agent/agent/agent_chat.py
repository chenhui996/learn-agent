# 目标：让 agent 具有记忆能力（memory）
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.redis import RedisSaver # 提供 redis 存储能力
from langgraph.prebuilt import create_react_agent # 创建智能体

from app.code_agent.model.qwen import llm_qwen
from app.code_agent.tools.file_tools import file_tools


# 创建智能体：
def create_agent():
    # 实例化一个 memory 对象

    with RedisSaver.from_conn_string("redis://localhost:6379") as memory:
        memory.setup()

        # 实例化一个智能体
        agent = create_react_agent(
            model=llm_qwen,
            tools=file_tools,
            checkpointer=memory,
            debug=True
        )

        return agent



def run_agent():
    config = RunnableConfig(configurable={"thread_id": "1"})

    agent = create_agent()

    res = agent.invoke(input={"messages": [("user", "我们刚才聊了什么？")]}, config=config)

    print("=" * 60)
    print(res)
    print("=" * 60)

    # res = agent.invoke(input={"messages": [("user", "我是谁？")]}, config=config)
    #
    # print("=" * 60)
    # print(res)
    # print("=" * 60)

if __name__ == "__main__":
    run_agent()

