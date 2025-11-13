import asyncio

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import StdioServerParameters, ClientSession, stdio_client
from langgraph.prebuilt import create_react_agent  # 官方现在更推荐的创建 code_agent 的方案

from app.bailian.common import llm


async def mcp_playwright_client():
    server_params = StdioServerParameters(
        command="npx",
        # args=["@playwright/mcp@latest"],
        args=["-y", "@executeautomation/playwright-mcp-server"]  # 版本要降到 1.0.3
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 等待服务器初始化
            await session.initialize()
            # 加载工具
            tools = await load_mcp_tools(session)
            # print(tools)

            agent = create_react_agent(model=llm, tools=tools, debug=False)
            response = await agent.ainvoke(input={"messages": [("user", "在搜狗中查询北京今天的天气")]})

            print(response)

            messages = response["messages"]
            for message in messages:
                print('---------------------------------')
                print('------------新一轮----------------')
                print('---------------------------------')
                if isinstance(message, HumanMessage):
                    print("用户:", message.content)
                elif isinstance(message, AIMessage):
                    if message.content:
                        print("助理:", message.content)
                    else:
                        for tool_call in message.tool_calls:
                            print("助理[调用工具]:", tool_call["name"], tool_call["args"])
                elif isinstance(message, ToolMessage):
                    print("调用工具", message.name)



asyncio.run(mcp_playwright_client())
