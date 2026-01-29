import subprocess
import sys
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ReloadHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        super().__init__()
        self.restart_callback = restart_callback

    def on_any_event(self, event):
        # 只在 .py 文件变化时重启
        if event.is_directory:
            return
        if event.src_path.endswith(".py"):
            print(f"[dev_runner] 检测到变更: {event.src_path}, 准备重启应用...")
            self.restart_callback()


def main():
    project_root = Path(__file__).parent
    app_process = None

    def start_app():
        nonlocal app_process
        if app_process is not None and app_process.poll() is None:
            return
        print("[dev_runner] 启动应用: python main.py")
        app_process = subprocess.Popen([sys.executable, "main.py"], cwd=str(project_root))

    def restart_app():
        nonlocal app_process
        if app_process is not None and app_process.poll() is None:
            print("[dev_runner] 终止旧进程...")
            app_process.terminate()
            try:
                app_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                app_process.kill()
        start_app()

    # 启动一次
    start_app()

    # 监听当前工程下的所有 .py 变化
    event_handler = ReloadHandler(restart_app)
    observer = Observer()
    observer.schedule(event_handler, str(project_root), recursive=True)
    observer.start()

    print("[dev_runner] 开发热重载已启动，修改 .py 文件会自动重启 main.py")

    try:
        while True:
            time.sleep(1)
            # 如果用户直接关掉应用窗口，子进程会退出，这里自动再拉起来
            if app_process is not None and app_process.poll() is not None:
                print("[dev_runner] 检测到应用退出，自动重新启动...")
                start_app()
    except KeyboardInterrupt:
        print("[dev_runner] 收到中断信号，退出...")
    finally:
        observer.stop()
        observer.join()
        if app_process is not None and app_process.poll() is None:
            app_process.terminate()


if __name__ == "__main__":
    main()

