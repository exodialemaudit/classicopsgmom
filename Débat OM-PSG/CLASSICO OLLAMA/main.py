import os
import sys
import time
import asyncio
import threading
from colorama import init, Fore, Back, Style
import streamlit.web.cli as stcli

def clear_console():
    """
    Nettoie la console de manière compatible avec Windows et Unix
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """
    Affiche une bannière ASCII au démarrage
    """
    banner = f"""
{Fore.CYAN} _______    ______    ______  
|       \\  /      \\  /      \\ 
| $$$$$$$\\|  $$$$$$\\|  $$$$$$\\
| $$__/ $$| $$___\\$$| $$ __\\$$
| $$    $$ \\$$    \\ | $$|    \\
| $$$$$$$  _\\$$$$$$\\| $$ \\$$$$
| $$      |  \\__| $$| $$__| $$
| $$       \\$$    $$ \\$$    $$
 \\$$        \\$$$$$$   \\$$$$$$ {Style.RESET_ALL}
"""
    print(banner)



def main():
    """
    Point d'entrée principal de l'application
    """
    # Initialiser colorama
    init()
    
    # Nettoyer la console
    clear_console()
    
    # Afficher la bannière
    print_banner()
    
    # Vérifier que le dossier debates existe
    if not os.path.exists('debates'):
        os.makedirs('debates')
        print(f"{Fore.GREEN}[✓] Dossier 'debates' créé{Style.RESET_ALL}")
    
    print(f"{Fore.YELLOW}[*] Démarrage de l'application...{Style.RESET_ALL}")
    time.sleep(1)
    

    # Démarrer l'application Streamlit
    print(f"{Fore.CYAN}[*] Lancement de l'interface web...{Style.RESET_ALL}")
    sys.argv = ["streamlit", "run", "frontend/app.py", "--server.port=490"]
    sys.exit(stcli.main())

if __name__ == '__main__':
    main() 