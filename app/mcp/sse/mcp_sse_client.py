import asyncio

from langchain.agents import initialize_agent, AgentType
from langchain_mcp_adapters.client import MultiServerMCPClient  # 专门用来创建 client，而且支持多种服务类型

from app.bailian.common import llm


async def create_mcp_sse_client():
    client = MultiServerMCPClient({
        "math_tools": {
            "url": "http://127.0.0.1:8000/sse",
            "transport": "sse",
        }
    })

    tools = await client.get_tools()
    print(tools)

    agent = initialize_agent(
        llm=llm,
        tools=tools,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    resp = await agent.ainvoke("1 + 2 * 5 = ?")

    return resp

asyncio.run(create_mcp_sse_client())