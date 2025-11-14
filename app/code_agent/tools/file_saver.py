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
        print("put")

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
        debug=True
    )

    config = RunnableConfig(configurable={"thread_id": 1})
    res = agent.invoke(input={"messages": "我是 Cain，你是谁？"}, config=config)
    print(res)
