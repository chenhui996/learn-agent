import json

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
        import pickle, base64
        pickled = pickle.dumps(data)
        return base64.b64encode(pickled).decode()

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Fetch a checkpoint tuple using the given configuration.

        Args:
            config: Configuration specifying which checkpoint to retrieve.

        Returns:
            Optional[CheckpointTuple]: The requested checkpoint tuple, or None if not found.
        """
        print("get_tuple")

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
        print("put_writes")
        pass


if __name__ == "__main__":
    memory = FileSaver()  # 实例化 file saver

    agent = create_react_agent(
        model=llm_qwen,
        tools=file_tools,
        checkpointer=memory,
        debug=False
    )

    config = RunnableConfig(configurable={"thread_id": 1})
    res = agent.invoke(input={"messages": "我是 Cain，你是谁？"}, config=config)
    print(res)
