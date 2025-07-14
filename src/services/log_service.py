from datetime import datetime
import os

class LogService:
    def __init__(self, repository, log_file="bot_scalping.log"):
        self.repo = repository
        self.log_file = log_file
        
        # Garante que o diretório existe
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def _write_to_file(self, level, message):
        """Escreve log no arquivo"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{level}] {timestamp} - {message}\n"
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Erro ao escrever no arquivo de log: {e}")

    def info(self, message):
        print(f"[INFO] {datetime.now()} - {message}")
        self._write_to_file("INFO", message)
        self.repo.save_log("INFO", message)

    def warn(self, message):
        print(f"[WARN] {datetime.now()} - {message}")
        self._write_to_file("WARN", message)
        self.repo.save_log("WARN", message)

    def error(self, message):
        print(f"[ERROR] {datetime.now()} - {message}")
        self._write_to_file("ERROR", message)
        self.repo.save_log("ERROR", message)

    def critical(self, message):
        print(f"[CRITICAL] {datetime.now()} - {message}")
        self._write_to_file("CRITICAL", message)
        self.repo.save_log("CRITICAL", message)
