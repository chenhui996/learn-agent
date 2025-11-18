import json
from pathlib import Path
import pickle, base64

from rich import print

import os
from typing import Optional, Sequence, Any

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver, CheckpointTuple, Checkpoint, CheckpointMetadata, \
    ChannelVersions
from langgraph.prebuilt import create_react_agent

from app.code_agent.tools.file_tools import file_tools
from app.code_agent.model.qwen import llm_qwen


class FileSaver(BaseCheckpointSaver[str]):
    def __init__(self, base_path: str = "/Users/chenhui/Downloads/agent/llm/.temp/checkpoint"):
        super().__init__()
        self.base_path = base_path

        os.makedirs(self.base_path, exist_ok=True)

    def _get_checkpoint_path(self, thread_id, checkpoint_id):
        dir_path = os.path.join(self.base_path, thread_id)  # 文件夹路径

        os.makedirs(dir_path, exist_ok=True)

        file_path = os.path.join(dir_path, checkpoint_id + '.json')  # 文件路径

        return file_path

    @staticmethod
    def _serialize_checkpoint(data) -> str:
        pickled = pickle.dumps(data)
        return base64.b64encode(pickled).decode()

    @staticmethod
    def _deserialize_data(data):
        decoded = base64.b64decode(data)  # 序列化：转换内容
        return pickle.loads(decoded)  # 再将转化后的内容，反序列化会原来的 对象结构

    # 根据持久化数据恢复记忆
    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        # 1. 找到正确的 checkpoint 文件路径
        thread_id = config["configurable"]["thread_id"]
        # checkpoint_id = config["configurable"].get("checkpoint_id")

        # 2. 读取 checkpoint 文件内容
        dir_path = os.path.join(self.base_path, thread_id)
        checkpoint_files = list(Path(dir_path).glob("*.json"))  # 利用内置的 Path 工具正则获取文件
        checkpoint_files.sort(key=lambda f: f.stem, reverse=True)

        if len(checkpoint_files) == 0:
            return None
        else:
            latest_checkpoint = checkpoint_files[0]  # 最新的 json 文件
            checkpoint_id = latest_checkpoint.stem  # 需要读取 文件的 id
            checkpoint_file_path = self._get_checkpoint_path(thread_id, checkpoint_id)  # 目标文件完整路径

            # 3. 对文件内容进行反序列化
            with open(checkpoint_file_path, "r", encoding="utf-8") as checkpoint_file:
                data = json.load(checkpoint_file)

            checkpoint = self._deserialize_data(data["checkpoint"])
            metadata = self._deserialize_data(data["metadata"])

            # 4. 返回 checkpoint 对象
            return CheckpointTuple(
                config={
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_id": checkpoint_id,
                    }
                },
                checkpoint=checkpoint,
                metadata=metadata,
            )

    # 将全量数据写入文件
    def put(
            self,
            config: RunnableConfig,
            checkpoint: Checkpoint,
            metadata: CheckpointMetadata,
            new_versions: ChannelVersions,
    ) -> RunnableConfig:
        # 1. 生成存储的 JSON 文件路径
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = checkpoint["id"]
        checkpoint_path = self._get_checkpoint_path(thread_id, checkpoint_id)  # JSON 文件存储路径

        # 2. 将 Checkpoint 进行序列化
        checkpoint_data = {
            "checkpoint": self._serialize_checkpoint(checkpoint),
            "metadata": self._serialize_checkpoint(metadata),
        }

        # 3. 将 Checkpoint 存储到文件系统
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)

        # 4. 生成返回值
        # print("put")
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
            }
        }

    # 写入增量数据（可以不实现）
    def put_writes(
            self,
            config: RunnableConfig,
            writes: Sequence[tuple[str, Any]],
            task_id: str,
            task_path: str = "",
    ) -> None:
        """Store intermediate writes linked to a checkpoint.

        Args:
            config: Configuration of the related checkpoint.
            writes: List of writes to store.
            task_id: Identifier for the task creating the writes.
            task_path: Path of the task creating the writes.
        """
        # print("put_writes")
        pass


if __name__ == "__main__":
    memory = FileSaver()  # 实例化 file saver

    agent = create_react_agent(
        model=llm_qwen,
        tools=file_tools,
        checkpointer=memory,
        debug=False
    )

    config = RunnableConfig(configurable={"thread_id": 2})

    while True:
        user_input = input("用户：")

        if user_input == "exit" or user_input == ":wq":
            break

        resp = agent.invoke(input={"messages": user_input}, config=config)
        print("助理：", resp["messages"][-1].content)
        print()
