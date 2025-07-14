from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.console import Group, Console
from rich.layout import Layout
from rich.text import Text
from time import sleep, time
import sys
from pathlib import Path
from dotenv import load_dotenv
sys.path.append(str(Path(__file__).parent.parent))

from repository.database_repository import DatabaseRepository
load_dotenv()
console = Console()

def criar_tabela_trades(trades):
    table = Table(title="📊 Últimos Trades Executados", expand=True)
    table.add_column("ID", justify="right")
    table.add_column("Par", justify="center")
    table.add_column("Tipo", justify="center")
    table.add_column("Preço", justify="right")
    table.add_column("Qtd", justify="right")
    table.add_column("Rebate", justify="right")
    table.add_column("P&L", justify="right")
    table.add_column("Timestamp", justify="center")

    for trade in trades[-10:]:
        table.add_row(
            str(trade[0]), trade[1], trade[2],
            f"{trade[3]:.4f}", f"{trade[4]:.4f}",
            f"{trade[5]:.4f}", f"{trade[6]:.4f}", trade[7]
        )
    return table

def painel_loop(intervalo=5):
    import os
    DATA_DIR = os.getenv("DATA_DIR")        
    db = DatabaseRepository(f"{DATA_DIR}/scalping.db")
    start_time = time()
    
    with Live(refresh_per_second=2, screen=True) as live:
        while True:
            trades = db.fetch_trades()
            pnl_total = sum(t[6] for t in trades)
            rebate_total = sum(t[5] for t in trades)

            header = Panel(Text(f"⏱️ Tempo: {int(time() - start_time)}s  |  💰 P&L Total: {pnl_total:.4f}  |  🎁 Rebates: {rebate_total:.4f}", justify='center', style="bold green"))

            body = criar_tabela_trades(trades)
            layout = Group(header, body)

            live.update(layout)
            sleep(intervalo)

if __name__ == "__main__":
    try:
        painel_loop()
    except KeyboardInterrupt:
        console.print("[bold red]⛔ Painel encerrado pelo usuário.[/bold red]")
