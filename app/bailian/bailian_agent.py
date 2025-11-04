import json

from langchain_core.output_parsers import JsonOutputParser  # 对返回结果进行标准化（JSON）
from langchain.agents import initialize_agent, AgentType
from pydantic import BaseModel, Field

from app.bailian.common import chart_prompt_template, create_calc_tools, llm


###########################################################################################

class Output(BaseModel):
    args: str = Field("调用工具时，提供给工具的具体参数值，用逗号分隔")
    result: str = Field("计算的结果")
    think: str = Field("思考过程")


parser = JsonOutputParser(pydantic_object=Output)
format_instructions = parser.get_format_instructions()
# print(format_instructions)

###########################################################################################

calc_tools = create_calc_tools()

# 智能体初始化
agent = initialize_agent(
    tools=calc_tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

###########################################################################################

# 使用提示词，约束大模型回答方向
prompt = chart_prompt_template.format_messages(
    role="计算",
    domain="使用工具进行数学计算",
    question=f"""
请阅读下面的问题，并返回一个严格的JSON对象，不要使用Markdown代码块包裹！
格式要求：
{format_instructions}

问题：
100+100=?
"""
)

###########################################################################################

resp = agent.invoke(prompt)

# print(resp)
print(resp["output"])
print(type(resp["output"]))
