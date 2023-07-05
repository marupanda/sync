import hashlib
import os
import shutil
import stat
import sys
import time
from typing import NamedTuple, Optional


# Remove directory and/or file if they exist
def remove_anyway(path):
    try:
        s = os.lstat(path).st_mode
        if stat.S_ISDIR(s):
            os.removedirs(path)
        else:
            os.remove(path)
    except IOError:
        pass


# Calculate "sha256" given a pth
def hash_file(path):
    try:
        with open(path, "rb") as f:
            return hashlib.file_digest(f, "sha256").digest()
    except IOError:
        pass


class File(NamedTuple):
    relative_path: str
    mode: int
    digest: Optional[str]


class Sync:
    def __init__(self, source_root, destination_root, log_file=sys.stdout):
        self.source_root = source_root
        self.destination_root = destination_root
        self.log_file = log_file
        self.source_files = []
        os.makedirs(self.destination_root, exist_ok=True)

    # Remove directory and/or file if there is any difference
    # between source and distination
    def clean_stale_files(self):
        for f in self.source_files:
            source_path = os.path.join(self.source_root, f.relative_path)
            destination_path = os.path.join(self.destination_root,
                                            f.relative_path)
            try:
                mode = os.lstat(source_path).st_mode
                if f.mode != mode:
                    remove_anyway(destination_path)
            except IOError:
                remove_anyway(destination_path)
        self.source_files.clear()

    # Synchronize source and destination folders
    def sync(self):
        self.clean_stale_files()
        for root, dirs, files in os.walk(self.source_root):
            for c in dirs + files:
                source_path = os.path.join(root, c)
                relative_path = os.path.relpath(source_path, self.source_root)
                destination_path = os.path.join(self.destination_root,
                                                relative_path)
                source_mode = os.lstat(source_path).st_mode
                if stat.S_ISDIR(source_mode):
                    os.makedirs(destination_path, exist_ok=True)
                    f = File(relative_path, source_mode, None)
                    self.source_files.append(f)
                else:
                    print(f"{source_path} -> {destination_path}",
                          file=self.log_file)
                    source_hash = hash_file(source_path)
                    destination_hash = hash_file(destination_path)
                    if source_hash != destination_hash:
                        shutil.copy2(source_path, destination_path)
                    f = File(relative_path, source_mode, source_hash)
                    self.source_files.append(f)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("synchronize two directories")
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("-i", "--interval", type=int, default=30)
    parser.add_argument("-l", "--log-file", type=argparse.FileType("w"))
    args = parser.parse_args()

    sync = Sync(args.source, args.destination, log_file=args.log_file)

    while True:
        sync.sync()
        time.sleep(args.interval)
