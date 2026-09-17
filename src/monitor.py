"""RPA - Watchdog folder monitoring for new invoice files."""

import shutil
import time
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer


class InvoiceHandler(FileSystemEventHandler):
    """Handler for new invoice files."""

    def __init__(self, callback: Callable[[Path], None], processed_dir: Path):
        super().__init__()
        self.callback = callback
        self.processed_dir = processed_dir
        self._processed_files: set[str] = set()

    def on_created(self, event: FileSystemEvent) -> None:
        """Called when a file is created."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process .txt files that haven't been processed yet
        if file_path.suffix.lower() == ".txt" and str(file_path) not in self._processed_files:
            self._processed_files.add(str(file_path))
            print(f"[MONITOR] New file detected: {file_path.name}")
            self.callback(file_path)


class Monitor:
    """RPA monitor using Watchdog to watch for new invoice files."""

    def __init__(self, inbox_dir: str | Path, processed_dir: str | Path):
        self.inbox_dir = Path(inbox_dir)
        self.processed_dir = Path(processed_dir)
        self.observer: Optional[Observer] = None
        self._handler: Optional[InvoiceHandler] = None

        # Ensure directories exist
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def start(self, callback: Callable[[Path], None]) -> None:
        """Start monitoring the inbox folder for new files."""
        self._handler = InvoiceHandler(callback, self.processed_dir)
        self.observer = Observer()
        self.observer.schedule(self._handler, str(self.inbox_dir), recursive=False)
        self.observer.start()
        print(f"[MONITOR] Watching folder: {self.inbox_dir}")

    def stop(self) -> None:
        """Stop monitoring."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("[MONITOR] Stopped")

    def move_to_processed(self, file_path: Path) -> Path:
        """Move a processed file to the processed directory."""
        destination = self.processed_dir / file_path.name
        shutil.move(str(file_path), str(destination))
        print(f"[MONITOR] Moved to processed: {destination}")
        return destination

    def process_existing_files(self, callback: Callable[[Path], None]) -> None:
        """Process any existing files in the inbox folder."""
        for file_path in self.inbox_dir.glob("*.txt"):
            print(f"[MONITOR] Processing existing file: {file_path.name}")
            callback(file_path)
