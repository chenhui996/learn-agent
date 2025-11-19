# mcp 相关的工具方法
from langchain_mcp_adapters.client import MultiServerMCPClient

# 创建并返回一个 stdio 类型的 mcp client
async def create_mcp_stdio_client(name, params):
    config = {
        name: {
            "transport": "stdio",
            **params
        }
    }

    print(config)
    client = MultiServerMCPClient(config)

    tools = await client.get_tools()

    return client, tools
