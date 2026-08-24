import os
import hashlib
from sys import prefix

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
    print('【1.0.1】', '【调用 百炼 API，用途：创建 百炼客户端的 配置项】，API 名称：【open_api_models】')

    # 具体实现
    # 1. 先有个配置
    config = open_api_models.Config(
        access_key_id=os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],  # 获取 阿里云的 access
        access_key_secret=os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'],  # 获取 阿里云的 access
    )
    config.endpoint = 'bailian.cn-beijing.aliyuncs.com'

    print('【1.0.2】', '【调用 百炼 API，用途：创建 百炼客户端】，API 名称：【bailian_20231229_client】')
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


# @mcp.tool(name="query_rag", description="从百炼平台查询知识库信息")
# def query_rag_from_bailian(
#         query: Annotated[str, Field(description="访问知识库查询的内容", examples=["终端的操作规范"])]) -> str:
#     client = create_client()  # 2. 实例化创建一个 百炼 SDK 客户端
#     print(client)
#     # 运行后若成功打印下面这种格式，证明创建成功
#     # <alibabacloud_bailian20231229.client.Client object at 0x10cc4f4d0>
#     workspace_id = 'llm-2bj8qis6czgv3sbc'  # 阿里云百炼 -> 业务空间id
#     index_id = 'miuptjzt11'  # 阿里云百炼 -> 知识库 id
#
#     rag = retrieve_index(client, workspace_id, index_id, query)
#
#     result = ""
#
#     for data in rag.body.data.nodes:
#         result += f"""{data.text}
# ---
# """
#     print("-" * 60)
#     print("[query_rag_from_bailian]", query)
#     print(result)
#     print("-" * 60)
#
#     return result


# 申请租约
def apply_lease(client, category_id, file_name, file_md5, file_size, workspace_id):
    header = {}
    runtime = util_models.RuntimeOptions()
    request = bailian_20231229_models.ApplyFileUploadLeaseRequest(
        file_name=file_name,
        md_5=file_md5,
        size_in_bytes=file_size,
    )

    print('【2.0.4】',
          '【调用 百炼 API，用途：获取 “用户租约” （lease）】，API 名称：【apply_file_upload_lease_with_options】')

    return client.apply_file_upload_lease_with_options(
        category_id,
        workspace_id,
        request,
        header,
        runtime
    )


def apply_lease_by_file_path(client, category_id, workspace_id, file_path):
    print('【2.0.3】',
          '【执行 函数：获取 “待上传文件的信息”，file_name, file_size, file_md5 这些文件信息】，函数名称：【get_file_info】')

    file_name, file_size, file_md5 = get_file_info(file_path)

    return apply_lease(client, category_id, file_name, file_md5, file_size, workspace_id)


def upload_file_to_bailian(upload_url, headers, file_path):
    with open(file_path, "rb") as f:
        file_content = f.read()

    upload_headers = {
        "Content-Type": headers["Content-Type"],
        "X-bailian-extra": headers["X-bailian-extra"],
    }

    print('【2.0.6】',
          '【调用 原生 API，用途：上传文件到 百炼 oss。因为租约中，告知了上传的 url 地址，所以只需要执行网络请求进行上传即可】，API 名称：【requests.put】')

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

    print('【2.0.7】',
          '【调用 百炼 API，用途：上传文件到具体 “类目” 下， 下一步执行完，刷新百炼对应页面，查看是否成功上传】，API 名称：【add_file_with_options】')

    return client.add_file_with_options(workspace_id, request, headers, runtime)


def describe_file(client, workspace_id, file_id):
    headers = {}
    runtime = util_models.RuntimeOptions()

    print('【2.0.9】', '【调用 百炼 API：查询已上传文件的 “详细信息”】，API名称：【describe_file_with_options】')

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

    print('【2.0.2】',
          '【执行 函数：获取百炼数据中心的 “文件租约”】，函数名称：【apply_lease_by_file_path】')

    # 获取百炼数据中心的 文件租约
    lease = apply_lease_by_file_path(client, category_id, workspace_id, file_path)

    print('【2.0.5】',
          '【租约 打印：lease”】', lease)

    # print(lease)

    headers = lease.body.data.param.headers
    lease_id = lease.body.data.file_upload_lease_id
    upload_url = lease.body.data.param.url
    parser = "DASHSCOPE_DOCMIND"

    # # 文件上传地址 阿里云百炼 给的
    # print('param', lease.body.data.param.url)

    # 上传文件到 百炼 oss
    upload_file_to_bailian(upload_url, headers, file_path)

    # 上传文件到具体类目下： 下一步执行完，刷新百炼数据中心页面，查看是否成功上传
    add_file_response = add_file_to_bailian_category(client, lease_id, parser, category_id, workspace_id)

    # 百炼中文件的 id：上传成功后，会自动创建
    file_id = add_file_response.body.data.file_id

    print('【2.0.8】', '【打印 对象，描述：百炼中 “已上传文件的 id”，上传成功后，会自动创建】，打印 对象：file_id', file_id)

    describe_file_response = describe_file(client, workspace_id, file_id)

    return describe_file_response


# 创建知识库：1. 创建索引
def create_index(
        client,
        workspace_id,
        name,
        file_id,
        structure_type="unstructured",  # 是否为结构化数据
        source_type="DATA_CENTER_FILE",  # 文件来源：默认就是数据中心
        sink_type="BUILT_IN"  # 知识库向量存储的类型
):
    headers = {}
    runtime = util_models.RuntimeOptions()

    request = bailian_20231229_models.CreateIndexRequest(
        structure_type=structure_type,
        source_type=source_type,
        sink_type=sink_type,
        name=name,
        description="学习用创建的知识库，创建时间：2026-08-23",
        document_ids=[file_id],  # 将文件给予 “向量化”
    )

    print('【3.0.2】','【调用 百炼 API，用途：创建具体的 知识库】','API名称：create_index_with_options')

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

    job_id = submit_index_add_documents_job_response.body.data.id

    # 获取该 “指向索引” 任务的指向情况
    job_status = get_index_job_status(client, workspace_id, index_id, job_id)
    # print(job_status.body.data)

    return job_status.body.data


@mcp.tool(name="query_rag", description="从百炼平台查询知识库信息")
def query_rag_from_bailian(
        query: Annotated[str, Field(description="访问知识库查询的内容", examples=[""])]) -> str:
    client = create_client()  # 2. 实例化创建一个 百炼 SDK 客户端
    print(client)
    # 运行后若成功打印下面这种格式，证明创建成功
    # <alibabacloud_bailian20231229.client.Client object at 0x10cc4f4d0>
    workspace_id = 'llm-2bj8qis6czgv3sbc'  # 阿里云百炼 -> 业务空间id
    index_id = '3prvi325h2'  # 阿里云百炼 -> 知识库 id

    rag = retrieve_index(client, workspace_id, index_id, query)

    result = ""

    for data in rag.body.data.nodes:
        result += f"""{data.text}
---
"""
    return result


@mcp.tool(name="upload_rag_from_local_file_path", description="将本地的知识文件上传到百炼平台")
def upload_rag_to_bailian(
        file_path: Annotated[
            str,
            Field(
                description="本地知识文件的路径，需要传入绝对路径",
                examples=["/Users/chenhui/Downloads/agent/lean-agent/app/code_agent/rag/rag_test02.txt"]
            )
        ]
):
    client = create_client()  # 实例化创建一个 百炼 SDK 客户端
    workspace_id = 'llm-2bj8qis6czgv3sbc'  # 阿里云百炼 -> 业务空间id
    category_id = "cate_9ec74c16bd614b4fa991a3d10b752267_12897951"  # 百炼类目名：智能体控制分类
    index_id = "3prvi325h2"  # 知识库 id：智能体控制知识库test3

    file_id = upload_rag_file_to_bailian(client, workspace_id, category_id, file_path)

    return add_document_to_index(client, workspace_id, index_id, file_id)


@mcp.tool(name="query_bailian_rag_job_status", description="查询上传到百炼知识库中的知识文件的处理状态")
def query_bailian_rag_job_status(
        job_id: Annotated[
            str,
            Field(
                description="处理此任务的 job_id",
                examples=["fd59508eccc043e18d70061717f86631"]
            )
        ]
):
    client = create_client()
    workspace_id = 'llm-2bj8qis6czgv3sbc'  # 阿里云百炼 -> 业务空间id
    index_id = "3prvi325h2"  # 知识库 id：智能体控制知识库test3

    # 获取该 “指向索引” 任务的指向情况
    job_status = get_index_job_status(client, workspace_id, index_id, job_id)

    return job_status


if __name__ == '__main__':
    # mcp.run(transport="stdio")

    print('-' * 6, '任务分割线', '-' * 120)

    # ------------------------------------------------------------------------------------------------

    print('【1.0.0】', '【任务 描述：创建 百炼客户端】','【必选任务】')

    # 测试: 上传知识到 百炼 RAG 知识库
    rag_file_path = "/Users/chenhui/Downloads/agent/learn-agent/app/code_agent/rag/rag_test02.txt"
    rag_category_id = "cate_16af1883cfb440c18bbb10f1f07bbb58_12897951"  # 官网 -> 应用 -> 数据连接 / 复习 RAG 之 2026-08-17 -> 百炼类目名：2026-08-17 demo1
    rag_workspace_id = 'llm-2bj8qis6czgv3sbc'  # 阿里云百炼 -> 业务空间id
    bailian_client = create_client()

    # 测试用例通过 -> 打印出 类似结构：<alibabacloud_bailian20231229.client.Client object at 0x10ca49010>
    print('【1.1.0】', '【创建 百炼客户端 成功】，打印创建的 bailian_client：', bailian_client)
    print('-' * 6, '任务分割线', '-' * 120)

    # ------------------------------------------------------------------------------------------------

    print('【2.0.0】',
          '【任务 描述：将本地的某个 测试文件，上传到 百炼 某个“数据连接” 下的某个 “类目”下】','【可选任务】')
    #
    # print('【2.0.1】',
    #       '【执行 函数：本任务的入口函数，也就是 “上传” 函数本身】，函数名称：【upload_rag_file_to_bailian】')
    #
    # # 上传 函数
    # file_response = upload_rag_file_to_bailian(bailian_client, rag_workspace_id, rag_category_id,
    #                                            rag_file_path)
    #
    # print('【2.1.0】',
    #       '【测试文件，已经被上传到 百炼的某个 “数据连接” 下的某个 “类目”】,打印 “文件详细信息”：',
    #       file_response)
    print('-' * 6, '任务分割线', '-' * 120)

    # ------------------------------------------------------------------------------------------------

    print('【3.0.0】','【任务 描述：增删改查 知识库】')

    print('【3.0.1】','【任务 描述：创建 知识库】','【可选任务】')

    # 创建知识库

    # 1. 创建知识库，获取知识库索引
    # response = create_index(bailian_client, rag_workspace_id, '智能体控制知识库test3-2026-08-23',
    #                         'file_db7c92bbc85a4c5389b2dd519cd9e06c_12897951')
    # print('【3.1.0】，【打印 描述：创建 知识库 完成，即将打印 “百炼创建成功后的 return 内容”：】',response)

    print('-' * 6, '任务分割线', '-' * 120)

    # ------------------------------------------------------------------------------------------------

    rag_index_id = "oac84j4cvy" # 上面 【3.1.0】创建的知识库的 专属ID

    print('【3.1.1】','【任务 描述：创建 知识库 后，指向索引（文件将会 “指向一份” 到该索引下】','直接使用【3.1.0】创建好的 知识库 id：', rag_index_id,'【可选任务】')

    # 2. 指向索引（文件将会 “指向一份” 到该索引下
    job_response = submit_index(bailian_client, rag_workspace_id, rag_index_id)
    job_id = job_response.body.data.id
    print(job_id)
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
