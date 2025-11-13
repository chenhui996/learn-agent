import os
import asyncio

from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.bailian.common import llm, file_tools


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

    print(file_tools)

    agent = initialize_agent(
        llm=llm,
        tools=tools + file_tools, # '+: 两个数组合并成一个数组'
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    prompt_template = PromptTemplate.from_template("你是一个智能助手，可以调用高德 MCP 工具。\n\n问题: {input}")
    prompt = prompt_template.format(input="""
目标：
- 明天上午10点，我要从 北京南站 到 北京望京SOHO
- 线路选择：公交地铁或打车
- 考虑出行时间和路线，以及天气状况和穿衣建议

要求：
- 制作网页来展示出行线路和位置，输出一个 HTML 页面到：/Users/chenhui/Downloads/code_agent/ai-code_agent-test/.temp，名称为：guide.html
- 网页使用简约美观的页面风格，以及卡片展示
- 行程规划的结果，要能够在 高德APP 中展示，并集成到 H5 页面中
""")
    print(prompt)

    resp = await agent.ainvoke(prompt)
    print(resp)

    return resp


asyncio.run(create_and_run_agent())
