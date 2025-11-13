from langchain_community.agent_toolkits.file_management import FileManagementToolkit

file_tools = FileManagementToolkit(root_dir='/Users/chenhui/Downloads/agent/llm/.temp').get_tools()