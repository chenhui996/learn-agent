import subprocess
import time


# 获取 terminal 的 window id
def get_all_terminal_window_ids():
    output, error = run_applescript("""
tell application "Terminal"
    set outputList to {}
    repeat with aWindow in windows
        set windowID to id of aWindow
        set tabCount to number of tabs of aWindow
        repeat with tabIndex from 1 to tabCount
            set end of outputList to {tab tabIndex of window id windowID}
        end repeat
    end repeat
end tell
return outputList
""")
    return output, error


def run_applescript(script):
    p = subprocess.Popen(["osascript", "-e", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()

    return output.decode("utf-8").strip(), error.decode("utf-8").strip()


# 关闭终端工具
def close_terminal_if_open():
    output, error = run_applescript("""
tell application "System Events"
    if exists process "Terminal" then
        tell application "Terminal" to quit
    end if
end tell
""")
    if error:
        return False
    else:
        return True


# 新增（打开）终端工具
def open_new_terminal(window_id: str = "") -> str:
    if window_id:
        output, error = run_applescript(f"""
tell application "Terminal"
    if (count of windows) > 0 then
        set theWindow to window id {window_id}
        set frontmost of theWindow to true
        activate
    else
        activate
    end if
end tell
""")
    else:
        output, error = run_applescript(f"""
tell application "Terminal"
    activate 
end tell
""")

    if error:
        return False
    else:
        time.sleep(5)
        return get_all_terminal_window_ids()


# 实现向终端输入脚本命令(可以理解为：自动打开终端，输入命令，且执行)
def run_script_in_terminal(script):
    output, error = run_applescript(f"""
tell application "Terminal"
    activate
    if(count of windows) > 0 then
        do script "{script}" in window 1
    else
        do script "{script}"
    end if 
end tell""")
    if error:
        return error
    else:
        return output

# 提供给智能体的工具：让 agent 知道我们执行了哪些命令
def get_terminal_full_text():
    output, error = run_applescript(f"""
    tell application "Terminal"
        set fullText to history of selected tab of front window
    end tell""")
    if error:
        return error
    else:
        return output


if __name__ == '__main__':
    # close_terminal_if_open()
    # window_ids = open_new_terminal()
    # print(window_ids)
    # run_script_in_terminal("pwd")
    full_text = get_terminal_full_text()
    print(full_text)
