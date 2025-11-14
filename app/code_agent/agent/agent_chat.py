from rich import print

# 目标：让 agent 具有记忆能力（memory）
import os

from langchain_core.runnables import RunnableConfig
# from langgraph.checkpoint.memory import MemorySaver # 提供 内存 存储能力
from langgraph.checkpoint.redis import RedisSaver  # 提供 redis 存储能力
from langgraph.checkpoint.mongodb import MongoDBSaver  # 提供 mongodb 存储能力
from langgraph.prebuilt import create_react_agent  # 创建智能体

from app.code_agent.model.qwen import llm_qwen
from app.code_agent.tools.file_tools import file_tools


# 创建智能体：
def run_agent():
    MONGODB_URI = os.environ.get("MONGODB_URI")
    MONGODB_DB = os.environ.get("MONGODB_DB")

    with MongoDBSaver.from_conn_string(MONGODB_URI, MONGODB_DB) as memory:
        # 实例化一个智能体
        agent = create_react_agent(
            model=llm_qwen,
            tools=file_tools,
            checkpointer=memory,
            debug=True
        )

        config = RunnableConfig(configurable={"thread_id": "1"})

        # res = agent.invoke(input={"messages": [("user", "我是 cain，你好")]}, config=config)
        #
        # print("=" * 60)
        # print(res)
        # print("=" * 60)

        res = agent.invoke(input={"messages": [("user", "ok，我再次来考考你的记忆力：我是谁？")]}, config=config)

        print("=" * 60)
        print(res)
        print("=" * 60)

        memory.close()


if __name__ == "__main__":
    run_agent()
