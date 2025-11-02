from dataclasses import Field

from langchain_openai import ChatOpenAI
from pydantic import StrictStr
from langchain_core.prompts import ChatMessagePromptTemplate
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.tools import tool
from pydantic import BaseModel, Field

############################################################################################################

llm = ChatOpenAI(
    model="qwen3-max",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=StrictStr("sk-cfb32d3791ba47cb915dfed7fe758cd9"),
    streaming=True,
)

############################################################################################################

system_message_template = ChatMessagePromptTemplate.from_template(
    template='你是一名{role}专家，擅长回答{domain}领域的问题',
    role="system"
)

user_message_template = ChatMessagePromptTemplate.from_template(
    template='用户问题：{question}',
    role="user"
)

# 创建提示词模版
chart_prompt_template = ChatPromptTemplate.from_messages([
    system_message_template,
    user_message_template
])


############################################################################################################

class CalcInputArgs(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

@tool(
    description="add two numbers",
    args_schema=CalcInputArgs,
    return_direct=True,
)
def add(a, b):
    return a + b

@tool(
    description="subtract two numbers",
    args_schema=CalcInputArgs,
    return_direct=True,
)
def subtract(a, b):
    return a - b

@tool(
    description="multiply two numbers",
    args_schema=CalcInputArgs,
    return_direct=True,
)
def multiply(a, b):
    return a * b

@tool(
    description="divide two numbers",
    args_schema=CalcInputArgs,
    return_direct=True,
)
def divide(a, b):
    return a / b

def create_calc_tools():
    return [add, subtract, multiply, divide]

calc_tools = create_calc_tools() # list[BaseTool]
