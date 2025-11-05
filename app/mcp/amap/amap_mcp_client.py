import os
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient


async def create_amap_mcp_client():
    amap_key = os.environ.get("AMAP_KEY")
    mcp_config = {
        "amap": {
            "url": f"https://mcp.amap.com/sse?key={amap_key}",
            "transport": "sse"
        }
    }

    client = MultiServerMCPClient(mcp_config)
    print(client)

    tools = await client.get_tools()
    print(tools)


asyncio.run(create_amap_mcp_client())
