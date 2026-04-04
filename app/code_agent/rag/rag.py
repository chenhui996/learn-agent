import os

import alibabacloud_bailian20231229
import alibabacloud_bailian20231229.client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_bailian20231229 import models as bailian_20231229_models
from alibabacloud_tea_util import models as util_models

# 获取 阿里云的 access
ALIBABA_CLOUD_ACCESS_KEY_ID = os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID']
ALIBABA_CLOUD_ACCESS_KEY_SECRET = os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET']

bailian_20231229_client = alibabacloud_bailian20231229.client.Client


# 创建一个百炼的客户端
def create_client() -> bailian_20231229_client:
    # 具体实现
    # 1. 先有个配置
    config = open_api_models.Config(
        access_key_id=ALIBABA_CLOUD_ACCESS_KEY_ID,
        access_key_secret=ALIBABA_CLOUD_ACCESS_KEY_SECRET,
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


if __name__ == '__main__':
    # 2. 实例化创建一个 百炼 SDK 客户端
    bailian_client = create_client()

    print(bailian_client)
    # 运行后若成功打印下面这种格式，证明创建成功
    # <alibabacloud_bailian20231229.client.Client object at 0x10cc4f4d0>

    # 3. 查询知识
    # 查询知识，最主要的，就是调用查询接口：retrieve，于是我们自己实现一个函数：retrieve_index
    workspace_id = 'llm-2bj8qis6czgv3sbc'  # 阿里云百炼 -> 业务空间id
    index_id = 'miuptjzt11'  # 阿里云百炼 -> 知识库 id
    query = '终端操作规范'  # 查询内容
    rag = retrieve_index(bailian_client, workspace_id, index_id, query)
    print(rag.body.data.nodes[0].text)
