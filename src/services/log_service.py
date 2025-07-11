from datetime import datetime

class LogService:
    def __init__(self, repository):
        self.repo = repository

    def info(self, message):
        print(f"[INFO] {datetime.now()} - {message}")
        self.repo.save_log("INFO", message)

    def warn(self, message):
        print(f"[WARN] {datetime.now()} - {message}")
        self.repo.save_log("WARN", message)

    def error(self, message):
        print(f"[ERROR] {datetime.now()} - {message}")
        self.repo.save_log("ERROR", message)

    def critical(self, message):
        print(f"[CRITICAL] {datetime.now()} - {message}")
        self.repo.save_log("CRITICAL", message)
