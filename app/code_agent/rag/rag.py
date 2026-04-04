import os

import alibabacloud_bailian20231229.client

from typing import Annotated
from pydantic import Field
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_bailian20231229 import models as bailian_20231229_models
from alibabacloud_tea_util import models as util_models
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

mcp = FastMCP()

load_dotenv()

bailian_20231229_client = alibabacloud_bailian20231229.client.Client


# 创建一个百炼的客户端
def create_client() -> bailian_20231229_client:
    # 具体实现
    # 1. 先有个配置
    config = open_api_models.Config(
        access_key_id=os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],  # 获取 阿里云的 access
        access_key_secret=os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'],  # 获取 阿里云的 access
    )
    config.endpoint = 'bailian.cn-beijing.aliyuncs.com'
    return bailian_20231229_client(config)


def retrieve_index(client, workspace_id, index_id, query):
    # 发起一个查询请求。
    # 写法没什么逻辑，就是百炼出的 “范式”，多看多写即可。
    retrieve_request = bailian_20231229_models.RetrieveRequest(
        index_id=index_id,
        query=query,
    )

    runtime = util_models.RuntimeOptions()

    return client.retrieve_with_options(
        workspace_id=workspace_id,
        tmp_req=retrieve_request,
        headers={},
        runtime=runtime,
    )


@mcp.tool(name="query_rag", description="从百炼平台查询知识库信息")
def query_rag_from_bailian(
        query: Annotated[str, Field(description="访问知识库查询的内容", examples=["终端的操作规范"])]) -> str:
    # 2. 实例化创建一个 百炼 SDK 客户端
    bailian_client = create_client()

    print(bailian_client)
    # 运行后若成功打印下面这种格式，证明创建成功
    # <alibabacloud_bailian20231229.client.Client object at 0x10cc4f4d0>

    workspace_id = 'llm-2bj8qis6czgv3sbc'  # 阿里云百炼 -> 业务空间id
    index_id = 'miuptjzt11'  # 阿里云百炼 -> 知识库 id
    rag = retrieve_index(bailian_client, workspace_id, index_id, query)

    result = ""

    for data in rag.body.data.nodes:
        result += f"""{data.text}
---
"""
    print("-" * 60)
    print("[query_rag_from_bailian]", query)
    print(result)
    print("-" * 60)

    return result


if __name__ == '__main__':
    mcp.run(transport="stdio")
    # 3. 查询知识
    # 查询知识，最主要的，就是调用查询接口：retrieve，于是我们自己实现一个函数：retrieve_index
    # query_text = '终端操作规范'  # 查询内容
    # rag_test = query_rag_from_bailian(query_text)
    # print(rag_test)
