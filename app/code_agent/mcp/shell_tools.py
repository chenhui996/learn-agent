import subprocess
import shlex


def run_shell_command(command):
    try:
        shell_command = shlex.split(command)
        if "rm" in shell_command:
            raise Exception("不允许使用rm")

        res = subprocess.run(command, shell=True, capture_output=True, text=True)

        if res.returncode != 0:
            return res.stderr
        return res.stdout
    except Exception as e:
        print(e)


def run_shell_command_by_popen(commands):
    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    stdout, stderr = p.communicate()
    return stdout, stderr


if __name__ == '__main__':
    # ret = run_shell_command("ls -al | grep terminal")
    success, failed = run_shell_command_by_popen("ls -al")
    print(success)
