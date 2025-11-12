import asyncio
import os

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import StdioServerParameters, ClientSession, stdio_client
from langgraph.prebuilt import create_react_agent  # 官方现在更推荐的创建 agent 的方案

from app.bailian.common import llm

async def mcp_playwright_client():
    server_params = StdioServerParameters(
        command="npx",
        # args=["@playwright/mcp@latest"],
        args=["-y", "@modelcontextprotocol/server-github"],
        env={
            "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 等待服务器初始化
            await session.initialize()
            # 加载工具
            tools = await load_mcp_tools(session)
            print(tools)

            agent = create_react_agent(model=llm, tools=tools, debug=True)
            response = await agent.ainvoke(input={"messages": [("user", "我的用户名是 chenhui996，查看一下有多少个公开的仓库，一共有多少star")]})

            print(response)

asyncio.run(mcp_playwright_client())
