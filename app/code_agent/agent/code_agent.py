import asyncio
import time

from langchain_core.messages import AIMessage, ToolMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from app.code_agent.model.qwen import llm_qwen
from app.code_agent.tools.file_saver import FileSaver
from app.code_agent.tools.file_tools import file_tools
from app.code_agent.tools.terminal_tools import get_stdio_terminal_tools


def format_debug_output(step_name: str, content: str, is_tool_call=False) -> None:
    if is_tool_call:
        print(f'🔄 【工具调用】 {step_name}')
        print("-" * 40)
        print(content.strip())
        print("-" * 40)
    else:
        print(f"💭 【{step_name}】")
        print("-" * 40)
        print(content.strip())
        print("-" * 40)


async def run_agent():
    memory = FileSaver()
    # memory = MemorySaver()

    # shell_tools = await get_stdio_shell_tools()
    terminal_tools = await get_stdio_terminal_tools()
    tools = file_tools + terminal_tools

    prompt = PromptTemplate.from_template(template="""
# 角色
你是一名优秀的工程师，你的名字叫做{name}

# 规范
## 使用 终端工具 执行 shell 命令的步骤，必须按照下列步骤执行：
- 步骤1: 调用 *关闭终端* 工具 close_terminal 关闭所有终端
- 步骤2: 打开一个新的终端，调用 *打开终端* 工具 open_terminal
- 步骤3: 向终端输入命令，调用 *运行终端脚本* 工具 run_terminal_script
- 步骤4: 这是最后才执行的一步，查看终端执行结果，调用 *获取终端文本* 工具 get_terminal_text
""")

    agent = create_react_agent(
        model=llm_qwen,
        tools=tools,
        checkpointer=memory,
        debug=False,
        prompt=SystemMessage(content=prompt.format(name="Bot")),
    )

    config = RunnableConfig(configurable={"thread_id": 563})

    while True:
        user_input = input("用户: ")

        if user_input.lower() == "exit":
            break

        print("\n🤖 助手正在思考...")
        print("=" * 60)

        iteration_count = 0
        start_time = time.time()
        last_tool_time = start_time

        # 从 RAG 知识库中读取知识，并拼接到提示词中

        async for chunk in agent.astream(input={"messages": user_input}, config=config):
            iteration_count += 1

            print(f"\n📊 第 {iteration_count} 步执行：")
            print("-" * 30)

            items = chunk.items()

            for node_name, node_output in items:
                if "messages" in node_output:
                    for msg in node_output["messages"]:
                        if isinstance(msg, AIMessage):
                            if msg.content:
                                format_debug_output("AI思考", msg.content)
                            else:
                                for tool in msg.tool_calls:
                                    format_debug_output("工具调用", f"{tool['name']}: {tool['args']}")

                        elif isinstance(msg, ToolMessage):
                            tool_name = getattr(msg, "name", "unknown")
                            tool_content = msg.content

                            current_time = time.time()
                            tool_duration = current_time - last_tool_time
                            last_tool_time = current_time

                            tool_result = f"""🔧 工具：{tool_name}
📤 结果：
{tool_content}
✅ 状态：执行完成，可以开始下一个任务
️⏱️ 执行时间：{tool_duration:.2f}秒"""

                            format_debug_output("工具执行结果", tool_result, is_tool_call=True)

                        else:
                            format_debug_output("未实现", f"暂未实现的打印内容: {chunk}")

        print()


asyncio.run(run_agent())
