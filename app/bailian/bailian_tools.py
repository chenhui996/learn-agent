from langchain_core.tools import tool
from pydantic import BaseModel, Field
from app.bailian.common import chart_prompt_template, llm

class AddInputArgs(BaseModel):
    number1: int = Field(description="first number")
    number2: int = Field(description="second number")

@tool(
    description="add two numbers",
    args_schema=AddInputArgs,
)
def add(number1, number2):
    return number1 + number2


# add_tools = Tool.from_function(
#     func=add,
#     name='add',
#     description='Add two numbers'
# )

tool_dict = {
    "add": add
}

# 绑定 tool
llm_with_tools = llm.bind_tools(tools=[add])

chain = chart_prompt_template | llm_with_tools

resp = chain.invoke(input={
    "role": "计算",
    "domain": "数学计算",
    "question": "使用工具计算：100+200=?"
})

print(resp)

# tool 会返回具体可执行的 物料，需要开发者自行实现具体操作
for tool_calls in resp.tool_calls:
    print(tool_calls)
    print('\n')

    args = tool_calls['args']
    print(args)

    func_name = tool_calls['name']
    print(func_name)

    tool_func = tool_dict[func_name]
    tool_content = tool_func.invoke(args)

    print(tool_content)
