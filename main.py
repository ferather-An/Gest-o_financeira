import sys
from PyQt5.QtWidgets import QApplication
from gui.login_window import LoginWindow
from database.db_manager import DatabaseManager

def main():
    # Inicializa a aplicação
    app = QApplication(sys.argv)
    
    # Configura o banco de dados
    db_manager = DatabaseManager()
    db_manager.setup_database()
    
    # Inicia com a tela de login
    login_window = LoginWindow()
    login_window.show()
    
    # Executa a aplicação
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()