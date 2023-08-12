import platform
import subprocess


system = platform.system()


def show_license():
    kwargs = {
        "shell": False,
        "stdin": None,
        "stdout": None,
        "stderr": None,
        "close_fds": True
    }
    if system == 'Windows':
        cmd = 'notepad'
        kwargs["creationflags"] = 0x00000008
    elif system == 'Darwin':
        cmd = 'open'
    else:
        cmd = 'xdg-open'
    subprocess.Popen([cmd, 'LICENSE.txt'], **kwargs)
