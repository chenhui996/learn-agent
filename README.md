# review

## anaconda

1. 装 anaconda
2. anaconda 安装一个新的 python 环境
3. gpt 问一下 anaconda 如何切环境
4. 装 uv

## uv

1. 装 uv：pip3
2. pip3 是装了 python 后，默认带的包管理器，用于安装 python 包
3. uv 安装依赖
4. 因为有 uv.lock 和 pyproject.toml，所以可以使用 uv 安装依赖
5. 安装的 shell 命令为：uv sync
6. 安装完成后，uv.lock 会更新为当前的依赖版本
7. 检查当前依赖是否安装成功：python 项目的目录下，生成了一个 .venv 目录，里面包含了当前项目的依赖

> 至此：项目依赖安装完成
