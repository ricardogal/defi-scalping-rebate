from repository.database_repository import DatabaseRepository
from rich.table import Table
from rich.console import Console
import json

def exibir_replay():
    db = DatabaseRepository()
    eventos = db.conn.execute("SELECT * FROM eventos ORDER BY timestamp ASC").fetchall()
    console = Console()
    table = Table(title="📜 Replay de Sessões")

    table.add_column("ID", justify="right")
    table.add_column("Tipo", justify="center")
    table.add_column("Par", justify="center")
    table.add_column("Mensagem", justify="left")
    table.add_column("Timestamp", justify="center")

    for ev in eventos[-50:]:
        table.add_row(str(ev[0]), ev[1], ev[2], ev[3], ev[5])

    console.print(table)
    db.close()

if __name__ == "__main__":
    exibir_replay()
