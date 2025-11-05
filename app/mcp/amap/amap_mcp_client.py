import os
import asyncio

from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.bailian.common import llm


async def create_amap_mcp_client():
    amap_key = os.getenv("AMAP_KEY")
    mcp_config = {
        "amap": {
            "url": f"https://mcp.amap.com/sse?key={amap_key}",
            "transport": "sse"
        }
    }

    client = MultiServerMCPClient(mcp_config)
    # print(client)

    tools = await client.get_tools()
    # print(tools)

    return client, tools


async def create_and_run_agent():
    client, tools = await create_amap_mcp_client()

    agent = initialize_agent(
        llm=llm,
        tools=tools,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    prompt_template = PromptTemplate.from_template("你是一个智能助手，可以调用高德 MCP 工具。\n\n问题: {input}")
    prompt = prompt_template.format(input="规划北京南站到北京望京SOHO的公交或地铁路线")
    print(prompt)

    resp = await agent.ainvoke(prompt)
    print(resp)

    return resp


asyncio.run(create_and_run_agent())
