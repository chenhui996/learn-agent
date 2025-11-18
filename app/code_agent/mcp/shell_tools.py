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


if __name__ == '__main__':
    ret = run_shell_command("ls -al | grep terminal")
    print(ret)
