import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler
import os
import shlex  # Add this import for properly splitting command arguments

# Split the command into individual arguments
# SCRIPT_TO_RUN = ["api", "populate", "--source_path", "~/BookStore-data_collection/data/output"]
SCRIPT_TO_RUN = ["tests/unit/test_carts.py"]
WATCH_DIRECTORY = "."
IGNORE_DIRECTORIES = {
    '__pycache__',
    '.git',
    'output',
    'venv',
    'env',
}


class ChangeHandler(PatternMatchingEventHandler):
    def __init__(self):
        # Set up patterns for ignoring directories
        ignore_patterns = [
            f"*/{dir_name}/*" for dir_name in IGNORE_DIRECTORIES]

        super().__init__(
            patterns=["*.py"],  # Only watch Python files
            ignore_patterns=ignore_patterns,
            ignore_directories=True,
            case_sensitive=True
        )

        self.process = None
        self.restart_script()

    def restart_script(self):
        if self.process:
            self.process.terminate()  # Terminate previous instance
            self.process.wait()
        print(f"Starting flask {' '.join(SCRIPT_TO_RUN)}...")

        # Pass flask as the first argument, followed by each argument in SCRIPT_TO_RUN
        command = ["pytest"] + SCRIPT_TO_RUN
        self.process = subprocess.Popen(command)

    def on_modified(self, event):
        if event.is_directory:
            return
        if any(ignored_dir in event.src_path for ignored_dir in IGNORE_DIRECTORIES):
            return
        print(f"File {event.src_path} changed. Restarting script...")
        self.restart_script()

    def on_created(self, event):
        if event.is_directory:
            return
        if any(ignored_dir in event.src_path for ignored_dir in IGNORE_DIRECTORIES):
            return
        print(f"New file {event.src_path} created. Restarting script...")
        self.restart_script()


if __name__ == "__main__":
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIRECTORY, recursive=True)
    print(f"Watching directory: {WATCH_DIRECTORY}")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()
