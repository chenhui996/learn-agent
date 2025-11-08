from mcp.server.fastmcp import FastMCP  # 将本地的 方法，变成一个 mcp 服务

# 01. 实例化一个 mcp
mcp = FastMCP("Math Tools")


# 02. 定义一个 mcp 工具
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

# 03. 将上面定义的东西，实现成为一个 mcp 服务
if __name__ == "__main__":
    mcp.run(transport="stdio")