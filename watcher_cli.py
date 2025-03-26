#!/usr/bin/env python3

import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import shlex
import click


class ChangeHandler(PatternMatchingEventHandler):
    def __init__(self, command, ignore_directories):
        ignore_patterns = [f"*/{dir_name}/*" for dir_name in ignore_directories]
        super().__init__(
            patterns=["*.py"],  # Only watch Python files
            ignore_patterns=ignore_patterns,
            ignore_directories=True,
            case_sensitive=True
        )
        self.command = shlex.split(command)
        self.process = None
        self.restart_command()

    def restart_command(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        self.process = subprocess.Popen(self.command)

    def on_modified(self, event):
        if not any(ignored in event.src_path for ignored in self.ignore_directories):
            self.restart_command()

    def on_created(self, event):
        if not any(ignored in event.src_path for ignored in self.ignore_directories):
            self.restart_command()


@click.command()
@click.argument("command", required=True)
@click.option("--watch-directory", default=".", help="Directory to watch for changes.")
@click.option("--ignore-directories", multiple=True, default=["__pycache__", ".git", "venv"],
              help="Directories to ignore.")
def main(command, watch_directory, ignore_directories):
    """
    A file watcher that restarts a command when Python files are modified or created.
    """
    event_handler = ChangeHandler(command, ignore_directories)
    observer = Observer()
    observer.schedule(event_handler, watch_directory, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()


if __name__ == "__main__":
    main()
