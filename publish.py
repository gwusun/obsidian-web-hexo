import os
import subprocess

os.chdir("/Users/sunwu/SW-Research/hexo-websit")
pipe = subprocess.Popen("make d",
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        bufsize=1)


# 实时打印log
def print_log_online():
    # 当info为b''时停止
    for info in iter(pipe.stderr.readline, b''):
        print(info)


print_log_online()
