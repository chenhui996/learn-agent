# 通过 bai lian 大模型调用 tools
from langchain_core.prompts import ChatPromptTemplate # 聊天提示词模版（组合定义好的角色）
from langchain_core.prompts import ChatMessagePromptTemplate # 定义某一角色
from langchain_core.prompts import FewShotPromptTemplate # 少样本提示模版
from langchain_core.prompts import PromptTemplate # 文本补全模型：生成单轮文本任务的提示
from langchain_openai import ChatOpenAI
from pydantic import StrictStr

############################################################################################################

llm = ChatOpenAI(
    model="qwen3-max",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=StrictStr("sk-cfb32d3791ba47cb915dfed7fe758cd9"),
    streaming=True,
)

############################################################################################################

# 角色 1
system_message_template = ChatMessagePromptTemplate.from_template(
    template='你是一名{role}专家，擅长回答{domain}领域的问题',
    role="system"
)

# 角色 2
user_message_template = ChatMessagePromptTemplate.from_template(
    template='用户问题：{question}',
    role="user"
)

# 创建提示词模版（组合 角色1 和 角色2）
chart_prompt_template = ChatPromptTemplate.from_messages([
    system_message_template,
    user_message_template
])

# 为上面的角色对话，注入参数
prompt = chart_prompt_template.format_messages(
    role="编程",
    domain="Web开发",
    question="你是谁？"
)

############################################################################################################

# 定义示例模板
example_template = '输入：{input}\n输出：{output}'

# 创建示例
examples = [
    {'input': "将 'Hello' 翻译成中文", 'output': '你好'},
    {'input': "将 'Goodbye' 翻译成中文", 'output': '再见'}
]

# 创建少样本模板
few_shot_prompt_template = FewShotPromptTemplate(
    examples=examples,
    example_prompt=PromptTemplate.from_template(example_template),
    prefix="请将以下英文翻译成中文：",
    suffix="输入：{text}\n输出：",
    input_variables=['text']
)

# 格式化提示
formatted_prompt = few_shot_prompt_template.format(text="Thank you")

print(formatted_prompt)

# resp = llm.stream(formatted_prompt)

############################################################################################################

# 链式调用
chain = few_shot_prompt_template | llm

resp = chain.stream(input={'text': 'Thank you'})

for chunk in resp:
    # print(chunk)
    print(chunk.content, end="")
