from langchain_experimental.utilities import PythonREPL

# 01. 生成 python_repl 实例
python_repl = PythonREPL()

# 02. 尝试执行 python 代码
ret =python_repl.run("print(1+1)")

print(ret)

# 03. 既然会用 repl 了，那，用 repl 写一个 PythonREPL 的 tools 试试