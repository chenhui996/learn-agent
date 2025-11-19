import subprocess
import shlex
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP()


@mcp.tool(name="run_shell", description="Run shell command")
def run_shell_command(command:
Annotated[str, Field(description="shell command will be executed", examples=["ls -al"])]) -> str:
    try:
        shell_command = shlex.split(command)
        if "rm" in shell_command:
            raise Exception("不允许使用rm")

        res = subprocess.run(command, shell=True, capture_output=True, text=True)

        if res.returncode != 0:
            return f"命令执行失败(退出码 {res.returncode}): {res.stderr.strip() or '未知错误'}"

        stdout = res.stdout.strip()
        stderr = res.stderr.strip()

        if stdout:
            return stdout
        elif stderr:
            return stderr
        else:
            # 关键:没有输出时,返回明确的成功消息
            return f"✓ 命令执行成功: {command}"
    except Exception as e:
        return str(e)


# def run_shell_command_by_popen(commands):
#     p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
#     stdout, stderr = p.communicate()
#     return stdout, stderr


if __name__ == '__main__':
    mcp.run(transport="stdio")
