# note

## 本 mcp 目录

- 存储了所有我们自己开发的 **mcp** 工具的目录，但这个工具并不会直接转换成 “langchain 可以调用的工具”

## 综上所述

- 创建完我们自己的 **mcp** 后，一定要去 **tools** 文件夹下： 
  - 将其转成 langchain 的 tool，供其调用。

## tools 文件夹

- 建立相应的方法，目的是：
  - 把 mcp 工具，转为 langchain 工具。

## 上述目的

- 转换后，能让 **大模型** 或者 **智能体**，能够直接调用。

## 完整链路文件

1. mcp文件：
   - /mcp/shell_tools.py
2. tools文件夹：
   - /tools/terminal_tools.py
3. 使用的智能体：
   - /agents/code_agent.py

## 细节知识

- **Annotated**：mcp 能够看懂的类型。