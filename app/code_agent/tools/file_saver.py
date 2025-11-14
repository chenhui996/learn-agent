import os
from langgraph.checkpoint.base import BaseCheckpointSaver


class FileSaver(BaseCheckpointSaver[str]):
    def __init__(self, base_path: str = "/Users/chenhui/Downloads/agent/llm/.temp/checkpoint"):
        super().__init__()
        self.base_path = base_path

        os.makedirs(self.base_path, exist_ok=True)

if __name__ == "__main__":
    saver = FileSaver() # 实例化 file saver