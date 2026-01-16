from langchain_openai import ChatOpenAI
from pydantic import StrictStr

############################################################################################################

llm_qwen = ChatOpenAI(
    model="qwen-max",
    # model="qwen3-235b-a22b",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=StrictStr("sk-cfb32d3791ba47cb915dfed7fe758cd9"),
    streaming=True,
)

############################################################################################################