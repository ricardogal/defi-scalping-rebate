#!/usr/bin/env python3
"""
Script principal para executar qualquer módulo do projeto
Adiciona automaticamente o src/ ao PYTHONPATH
"""

import sys
import os
from pathlib import Path

# Adiciona src/ ao PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Carrega variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python run.py <script>")
        print("Exemplos:")
        print("  python run.py main")
        print("  python run.py cancelador")
        print("  python run.py painel")
        print("  python run.py stop")
        sys.exit(1)
    
    script = sys.argv[1]
    
    # Importa e executa o script
    try:
        if script == "main":
            from main import main
            main()
        elif script == "cancelador":
            from controle.cancelador_ordens import cancelar_ordens_pendentes
            cancelar_ordens_pendentes()
        elif script == "painel":
            from painel.painel_live import painel_loop
            painel_loop()
        elif script == "stop":
            from stop_bot import stop_bot
            stop_bot()
        else:
            print(f"Script '{script}' não reconhecido")
            print("Scripts disponíveis: main, cancelador, painel, stop")
            sys.exit(1)
    except Exception as e:
        print(f"Erro ao executar {script}: {e}")
        sys.exit(1) 