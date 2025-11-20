import subprocess


def run_applescript(script):
    p = subprocess.Popen(["osascript", "-e", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()

    return output.decode("utf-8").strip(), error.decode("utf-8").strip()


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


if __name__ == '__main__':
    close_terminal_if_open()
