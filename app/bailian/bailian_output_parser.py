from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser
from app.bailian.common import chart_prompt_template, llm

####################################################################################

# 01. 纯字符串 parser
parser = StrOutputParser()
chain = chart_prompt_template | llm | parser

resp = chain.invoke(input={
    "role": "计算",
    "domain": "数学计算",
    "question": "100*100=?"
})

print(resp)

####################################################################################

# 02. 数组分割 parser
parserCom = CommaSeparatedListOutputParser()
chainCom = chart_prompt_template | llm | parserCom

respCom = chainCom.invoke(input={
    "role": "计算",
    "domain": "数学计算",
    "question": "100*100=?"
})

print(respCom)

####################################################################################