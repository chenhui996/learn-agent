import os
import hashlib
import alibabacloud_bailian20231229.client

from typing import Annotated

import requests
from pydantic import Field
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_bailian20231229 import models as bailian_20231229_models
from alibabacloud_tea_util import models as util_models
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

mcp = FastMCP()

load_dotenv()

bailian_20231229_client = alibabacloud_bailian20231229.client.Client


def calculate_md5(file_path: str) -> str:
    """
    计算文件的 MD5 哈希值。

    参数:
        file_path (str): 文件路径。

    返回:
        str: 文件的 MD5 哈希值。
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_file_info(file_path):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    file_md5 = calculate_md5(file_path)

    return file_name, file_size, file_md5


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
    client = create_client()  # 2. 实例化创建一个 百炼 SDK 客户端
    print(client)
    # 运行后若成功打印下面这种格式，证明创建成功
    # <alibabacloud_bailian20231229.client.Client object at 0x10cc4f4d0>
    workspace_id = 'llm-2bj8qis6czgv3sbc'  # 阿里云百炼 -> 业务空间id
    index_id = 'miuptjzt11'  # 阿里云百炼 -> 知识库 id

    rag = retrieve_index(client, workspace_id, index_id, query)

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


# 申请租约
def apply_lease(client, category_id, file_name, file_md5, file_size, workspace_id):
    header = {}
    runtime = util_models.RuntimeOptions()
    request = bailian_20231229_models.ApplyFileUploadLeaseRequest(
        file_name=file_name,
        md_5=file_md5,
        size_in_bytes=file_size,
    )
    return client.apply_file_upload_lease_with_options(
        category_id,
        workspace_id,
        request,
        header,
        runtime
    )


def apply_lease_by_file_path(client, category_id, workspace_id, file_path):
    file_name, file_size, file_md5 = get_file_info(file_path)

    return apply_lease(client, category_id, file_name, file_md5, file_size, workspace_id)


def upload_file_to_bailian(upload_url, headers, file_path):
    with open(file_path, "rb") as f:
        file_content = f.read()

    upload_headers = {
        "Content-Type": headers["Content-Type"],
        "X-bailian-extra": headers["X-bailian-extra"],
    }

    response = requests.put(upload_url, data=file_content, headers=upload_headers)
    # print(response.status_code)
    response.raise_for_status()


def add_file_to_bailian_category(client, lease_id, parser, category_id, workspace_id):
    headers = {}
    runtime = util_models.RuntimeOptions()

    request = bailian_20231229_models.AddFileRequest(
        parser=parser,
        lease_id=lease_id,
        category_id=category_id,
    )

    return client.add_file_with_options(workspace_id, request, headers, runtime)


def describe_file(client, workspace_id, file_id):
    headers = {}
    runtime = util_models.RuntimeOptions()

    return client.describe_file_with_options(workspace_id, file_id, headers, runtime)


# 上传知识到 百炼 RAG 知识库
def upload_rag_file_to_bailian(client, workspace_id, category_id, file_path):
    """
    上传文件到百炼数据中心，并添加到指定分类
    
    params:
        client: 百炼 客户端
        workspace_id: 百炼 业务空间ID（一级）
        category_id: 百炼 分类ID（二级）
        file_path: 本地 待上传的 文件路径
    return:
        file props: 文件上传状态
    """

    # 获取百炼数据中心的 文件租约
    lease = apply_lease_by_file_path(client, category_id, workspace_id, file_path)

    headers = lease.body.data.param.headers
    lease_id = lease.body.data.file_upload_lease_id
    upload_url = lease.body.data.param.url
    parser = "DASHSCOPE_DOCMIND"

    # 上传文件到 百炼 oss
    upload_file_to_bailian(upload_url, headers, file_path)

    # 上传文件到具体类目下： 下一步执行完，刷新百炼数据中心页面，查看是否成功上传
    add_file_response = add_file_to_bailian_category(client, lease_id, parser, category_id, workspace_id)

    # 百炼中文件的 id：上传成功后，会自动创建
    file_id = add_file_response.body.data.file_id

    # 文件 props 信息：通过 file_id 查询到的文件属性信息
    describe_file_response = describe_file(client, workspace_id, file_id)
    print(describe_file_response)

    return describe_file_response


# 创建知识库：1. 创建索引
def create_index(
        client,
        workspace_id,
        name,
        file_id,
        structure_type="unstructured",
        source_type="DATA_CENTER_FILE",
        sink_type="BUILT_IN"):
    headers = {}
    runtime = util_models.RuntimeOptions()

    request = bailian_20231229_models.CreateIndexRequest(
        structure_type=structure_type,
        source_type=source_type,
        sink_type=sink_type,
        name=name,
        document_ids=[file_id],  # 将文件给予 “向量化”
    )

    return client.create_index_with_options(workspace_id, request, headers, runtime)


# 创建知识库：2. 指向索引
def submit_index(client, workspace_id, index_id):
    headers = {}
    runtime = util_models.RuntimeOptions()

    submit_index_job_request = bailian_20231229_models.SubmitIndexJobRequest(index_id=index_id)

    return client.submit_index_job_with_options(workspace_id, submit_index_job_request, headers, runtime)


#  创建知识库：3. 访问索引状态
def get_index_job_status(client, workspace_id, index_id, job_id):
    headers = {}
    runtime = util_models.RuntimeOptions()

    get_index_job_status_request = bailian_20231229_models.GetIndexJobStatusRequest(
        index_id=index_id,
        job_id=job_id,
    )

    return client.get_index_job_status_with_options(workspace_id, get_index_job_status_request, headers, runtime)


# 查询知识库：当前工作空间下的所有知识库信息
def list_indices(client, workspace_id):
    headers = {}
    runtime = util_models.RuntimeOptions()

    list_indices_request = bailian_20231229_models.ListIndicesRequest()

    return client.list_indices_with_options(workspace_id, list_indices_request, headers, runtime)


# 增量文件到添加知识库
def submit_index_add_documents_job(
        client,
        workspace_id,
        index_id,
        file_id,
        source_type="DATA_CENTER_FILE"
):
    headers = {}
    runtime = util_models.RuntimeOptions()
    submit_index_add_documents_job_request = bailian_20231229_models.SubmitIndexAddDocumentsJobRequest(
        index_id=index_id,
        source_type=source_type,
        document_ids=[file_id],
    )

    return client.submit_index_add_documents_job_with_options(workspace_id, submit_index_add_documents_job_request,
                                                              headers,
                                                              runtime)

# 封装多流程：增量文件到添加知识库
def add_document_to_index(client, workspace_id, index_id, file_id):
    submit_index_add_documents_job_response = submit_index_add_documents_job(
        client,
        workspace_id,
        index_id,
        file_id,
    )

    job_id = submit_index_add_documents_job_response.body.id

    # 获取该 “指向索引” 任务的指向情况
    job_status = get_index_job_status(client, workspace_id, index_id, job_id)
    print(job_status.body.data)


if __name__ == '__main__':
    # mcp.run(transport="stdio")

    # ------------------------------------------------------------------------------------------------

    # 测试: 上传知识到 百炼 RAG 知识库
    rag_file_path = "/Users/chenhui/Downloads/agent/ai-agent-test/app/code_agent/rag/rag_test.txt"
    rag_category_id = "cate_9ec74c16bd614b4fa991a3d10b752267_12897951"  # 百炼类目名：智能体控制分类
    rag_workspace_id = 'llm-2bj8qis6czgv3sbc'  # 阿里云百炼 -> 业务空间id
    bailian_client = create_client()

    # ------------------------------------------------------------------------------------------------

    # 上传 函数
    # file_response = upload_rag_file_to_bailian(bailian_client, rag_workspace_id, rag_category_id,
    #                                            rag_file_path)

    # ------------------------------------------------------------------------------------------------

    # 创建知识库

    # 1. 创建知识库，获取知识库索引
    # response = create_index(bailian_client, rag_workspace_id, '智能体控制知识库test3',
    #                         'file_b1a46892999d48ca9a6ee40592908d4e_12897951')
    # print(response)
    rag_index_id = "3prvi325h2"

    # 2. 指向索引（文件将会 “指向一份” 到该索引下
    # job_response = submit_index(bailian_client, rag_workspace_id, rag_index_id)
    # job_id = job_response.body.data.id
    # print(job_id)
    # rag_job_id = "dc9bb19f4911427787382ce69b7b29a0"

    # 3. 获取该 “指向索引” 任务的指向情况
    # job_status = get_index_job_status(bailian_client, rag_workspace_id, rag_index_id, rag_job_id)
    # print(job_status.body.data)

    # ------------------------------------------------------------------------------------------------

    # 查询知识库：当前工作空间下的所有知识库信息
    # list_indices_response = list_indices(bailian_client, rag_workspace_id)
    #
    # print(list_indices_response)

    # ------------------------------------------------------------------------------------------------

    # 添加增量文件到指定知识库下（向量化）

    # rag_file_id = "file_94f8031c7de44be28cb27a487ea850ff_12897951"
    # submit_index_add_documents_job_response = submit_index_add_documents_job(
    #     bailian_client,
    #     rag_workspace_id,
    #     rag_index_id,
    #     rag_file_id,
    # )

    # print(submit_index_add_documents_job_response)

    # rag_job_id = "08e42839bf35491080e0159f5249a875"
    # # 获取该 “指向索引” 任务的指向情况
    # job_status = get_index_job_status(bailian_client, rag_workspace_id, rag_index_id, rag_job_id)
    # print(job_status.body.data)

    # ------------------------------------------------------------------------------------------------
