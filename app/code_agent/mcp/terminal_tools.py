import subprocess


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
        return get_all_terminal_window_ids()

if __name__ == '__main__':
    close_terminal_if_open()
    window_ids = open_new_terminal()
    print(window_ids)
