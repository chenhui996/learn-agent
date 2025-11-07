from dataclasses import Field

from langchain_openai import ChatOpenAI
from pydantic import StrictStr
from langchain_core.prompts import ChatMessagePromptTemplate
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from langchain_community.agent_toolkits import FileManagementToolkit # 工具包

############################################################################################################

llm = ChatOpenAI(
    # model="qwen3-max",
    model="qwen3-235b-a22b",
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
    return_direct=False,
)
def add(a, b):
    return a + b

def create_calc_tools():
    return [add]

calc_tools = create_calc_tools() # list[BaseTool]

file_toolkit = FileManagementToolkit(root_dir="/Users/chenhui/Downloads/aiAgent/ai-agent-test/.temp")
file_tools = file_toolkit.get_tools()
