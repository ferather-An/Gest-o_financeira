import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from auth.auth_manager import AuthManager
from gui.register_screen import RegisterScreen
from gui.main_window import MainWindow

class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        self.auth_manager = AuthManager()
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Sistema de Gestão Financeira - Login")
        self.setFixedSize(800, 500)
        
        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Painel esquerdo (imagem/logo)
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #9370DB;")
        left_panel.setFixedWidth(400)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # Logo/título
        logo_label = QLabel("Sistema de\nGestão Financeira")
        logo_label.setFont(QFont("Arial", 24, QFont.Bold))
        logo_label.setStyleSheet("color: white;")
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Subtítulo
        subtitle_label = QLabel("Controle suas finanças com facilidade")
        subtitle_label.setFont(QFont("Arial", 14))
        subtitle_label.setStyleSheet("color: white;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        left_layout.addWidget(logo_label)
        left_layout.addSpacing(20)
        left_layout.addWidget(subtitle_label)
        
        # Painel direito (formulário de login)
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: white;")
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(50, 50, 50, 50)
        right_layout.setAlignment(Qt.AlignCenter)
        
        # Título do formulário
        form_title = QLabel("Login")
        form_title.setFont(QFont("Arial", 20, QFont.Bold))
        form_title.setAlignment(Qt.AlignCenter)
        
        # Campo de usuário
        username_label = QLabel("Usuário:")
        username_label.setFont(QFont("Arial", 12))
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Digite seu nome de usuário")
        self.username_input.setMinimumHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #9370DB;
            }
        """)
        
        # Campo de senha
        password_label = QLabel("Senha:")
        password_label.setFont(QFont("Arial", 12))
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #9370DB;
            }
        """)
        
        # Botão de login
        login_button = QPushButton("Entrar")
        login_button.setMinimumHeight(40)
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #9370DB;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8A2BE2;
            }
        """)
        login_button.clicked.connect(self.login)
        
        # Link para cadastro
        register_layout = QHBoxLayout()
        register_layout.setAlignment(Qt.AlignCenter)
        
        register_label = QLabel("Não tem uma conta?")
        register_label.setFont(QFont("Arial", 10))
        
        register_link = QPushButton("Cadastre-se")
        register_link.setFlat(True)
        register_link.setCursor(Qt.PointingHandCursor)
        register_link.setStyleSheet("""
            QPushButton {
                color: #9370DB;
                font-weight: bold;
                border: none;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #8A2BE2;
            }
        """)
        register_link.clicked.connect(self.show_register_screen)
        
        register_layout.addWidget(register_label)
        register_layout.addWidget(register_link)
        
        # Adiciona os widgets ao layout direito
        right_layout.addWidget(form_title)
        right_layout.addSpacing(30)
        right_layout.addWidget(username_label)
        right_layout.addWidget(self.username_input)
        right_layout.addSpacing(20)
        right_layout.addWidget(password_label)
        right_layout.addWidget(self.password_input)
        right_layout.addSpacing(30)
        right_layout.addWidget(login_button)
        right_layout.addSpacing(20)
        right_layout.addLayout(register_layout)
        
        # Adiciona os painéis ao layout principal
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
    
    def login(self):
        """Realiza o login do usuário"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Campos vazios", "Por favor, preencha todos os campos.")
            return
        
        if self.auth_manager.login(username, password):
            # Login bem-sucedido, abre a janela principal
            self.main_window = MainWindow(self.auth_manager)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Erro de login", "Usuário ou senha incorretos.")
    
    def show_register_screen(self):
        """Exibe a tela de cadastro"""
        self.register_screen = RegisterScreen(self.auth_manager)
        self.register_screen.show()
        self.close()