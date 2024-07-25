import os
import time

if os.name == "nt":
    import msvcrt

    def lock(fp):
        fp.seek(0)
        msvcrt.locking(fp.fileno(), msvcrt.LK_LOCK, 1)

    def unlock(fp):
        fp.seek(0)
        msvcrt.locking(fp.fileno(), msvcrt.LK_UNLCK, 1)

else:
    import fcntl

    def lock(fp):
        fcntl.flock(fp.fileno(), fcntl.LOCK_EX)

    def unlock(fp):
        fcntl.flock(fp.fileno(), fcntl.LOCK_UN)


class Locker:
    def __init__(self, lck_name: str):
        self.lck_path = os.path.join(
            os.path.expanduser("~"), ".rfuniverse", lck_name + ".lck"
        )
        # check if the lock file exists
        if not os.path.exists(self.lck_path):
            os.makedirs(os.path.dirname(self.lck_path), exist_ok=True)
            open(self.lck_path, "w+").close()
        self.fp = None

    def __enter__(self):
        self.fp = open(self.lck_path, 'r+')  # Open the file in read-write mode
        lock(self.fp)
        return self.fp

    def __exit__(self, _type, value, tb):
        try:
            unlock(self.fp)
        finally:
            self.fp.close()
        time.sleep(0.1)
