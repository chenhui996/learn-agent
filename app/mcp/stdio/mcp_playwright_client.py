import asyncio

from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import StdioServerParameters, ClientSession, stdio_client

async def mcp_playwright_client():
    server_params = StdioServerParameters(
        command="npx",
        # args=["@playwright/mcp@latest"],
        args=["-y", "@executeautomation/playwright-mcp-server"] # 版本要降到 1.0.3
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 等待服务器初始化
            await session.initialize()
            # 加载工具
            tools = await load_mcp_tools(session)
            print(tools)


asyncio.run(mcp_playwright_client())
