from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QStackedWidget, 
                            QMessageBox, QFormLayout, QGroupBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from auth.auth_manager import AuthManager
from gui.main_window import MainWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.auth_manager = AuthManager()
        
        self.setWindowTitle("Sistema de Gestão Financeira - Login")
        self.setMinimumSize(800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Área de imagem/logo (lado esquerdo)
        logo_layout = QVBoxLayout()
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Cria um pixmap roxo com texto
        pixmap = QPixmap(400, 600)
        pixmap.fill(Qt.transparent)
        logo_label.setPixmap(pixmap)
        logo_label.setStyleSheet("background-color: #9370DB; border-radius: 10px;")
        
        # Adiciona texto ao logo
        title_label = QLabel("Sistema de Gestão Financeira")
        title_label.setStyleSheet("color: white; background-color: transparent;")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Controle suas finanças com facilidade")
        subtitle_label.setStyleSheet("color: white; background-color: transparent;")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        logo_layout.addStretch()
        logo_layout.addWidget(title_label)
        logo_layout.addWidget(subtitle_label)
        logo_layout.addStretch()
        
        # Área de login/cadastro (lado direito)
        self.auth_stack = QStackedWidget()
        
        # Página de login
        login_widget = QWidget()
        login_layout = QVBoxLayout(login_widget)
        login_layout.setContentsMargins(50, 50, 50, 50)
        
        login_title = QLabel("Login")
        login_title.setFont(QFont("Arial", 16, QFont.Bold))
        login_title.setAlignment(Qt.AlignCenter)
        
        login_form = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nome de usuário")
        self.username_input.setMinimumHeight(40)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        
        login_form.addRow("Usuário:", self.username_input)
        login_form.addRow("Senha:", self.password_input)
        
        login_button = QPushButton("Entrar")
        login_button.setMinimumHeight(40)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #9370DB;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8A2BE2;
            }
        """)
        login_button.clicked.connect(self.login)
        
        register_link = QPushButton("Não tem uma conta? Cadastre-se")
        register_link.setFlat(True)
        register_link.setCursor(Qt.PointingHandCursor)
        register_link.clicked.connect(lambda: self.auth_stack.setCurrentIndex(1))
        
        login_layout.addWidget(login_title)
        login_layout.addSpacing(30)
        login_layout.addLayout(login_form)
        login_layout.addSpacing(20)
        login_layout.addWidget(login_button)
        login_layout.addWidget(register_link, alignment=Qt.AlignCenter)
        login_layout.addStretch()
        
        # Página de cadastro
        register_widget = QWidget()
        register_layout = QVBoxLayout(register_widget)
        register_layout.setContentsMargins(50, 50, 50, 50)
        
        register_title = QLabel("Cadastro")
        register_title.setFont(QFont("Arial", 16, QFont.Bold))
        register_title.setAlignment(Qt.AlignCenter)
        
        register_form = QFormLayout()
        
        self.reg_fullname_input = QLineEdit()
        self.reg_fullname_input.setPlaceholderText("Nome completo")
        self.reg_fullname_input.setMinimumHeight(40)
        
        self.reg_username_input = QLineEdit()
        self.reg_username_input.setPlaceholderText("Nome de usuário")
        self.reg_username_input.setMinimumHeight(40)
        
        self.reg_email_input = QLineEdit()
        self.reg_email_input.setPlaceholderText("E-mail")
        self.reg_email_input.setMinimumHeight(40)
        
        self.reg_password_input = QLineEdit()
        self.reg_password_input.setPlaceholderText("Senha")
        self.reg_password_input.setEchoMode(QLineEdit.Password)
        self.reg_password_input.setMinimumHeight(40)
        
        self.reg_confirm_password_input = QLineEdit()
        self.reg_confirm_password_input.setPlaceholderText("Confirmar senha")
        self.reg_confirm_password_input.setEchoMode(QLineEdit.Password)
        self.reg_confirm_password_input.setMinimumHeight(40)
        
        register_form.addRow("Nome completo:", self.reg_fullname_input)
        register_form.addRow("Usuário:", self.reg_username_input)
        register_form.addRow("E-mail:", self.reg_email_input)
        register_form.addRow("Senha:", self.reg_password_input)
        register_form.addRow("Confirmar senha:", self.reg_confirm_password_input)
        
        register_button = QPushButton("Cadastrar")
        register_button.setMinimumHeight(40)
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #9370DB;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8A2BE2;
            }
        """)
        register_button.clicked.connect(self.register)
        
        login_link = QPushButton("Já tem uma conta? Faça login")
        login_link.setFlat(True)
        login_link.setCursor(Qt.PointingHandCursor)
        login_link.clicked.connect(lambda: self.auth_stack.setCurrentIndex(0))
        
        register_layout.addWidget(register_title)
        register_layout.addSpacing(20)
        register_layout.addLayout(register_form)
        register_layout.addSpacing(20)
        register_layout.addWidget(register_button)
        register_layout.addWidget(login_link, alignment=Qt.AlignCenter)
        register_layout.addStretch()
        
        # Adiciona as páginas ao stack
        self.auth_stack.addWidget(login_widget)
        self.auth_stack.addWidget(register_widget)
        
        # Adiciona os layouts ao layout principal
        main_layout.addLayout(logo_layout, 1)
        main_layout.addWidget(self.auth_stack, 1)
        
        # Estiliza a janela
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QLabel {
                font-family: Arial;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #9370DB;
            }
        """)
    
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
    
    def register(self):
        """Registra um novo usuário"""
        fullname = self.reg_fullname_input.text()
        username = self.reg_username_input.text()
        email = self.reg_email_input.text()
        password = self.reg_password_input.text()
        confirm_password = self.reg_confirm_password_input.text()
        
        # Validações básicas
        if not fullname or not username or not password or not confirm_password:
            QMessageBox.warning(self, "Campos vazios", "Por favor, preencha todos os campos obrigatórios.")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Senhas diferentes", "As senhas não coincidem.")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Senha fraca", "A senha deve ter pelo menos 6 caracteres.")
            return
        
        # Tenta registrar o usuário
        if self.auth_manager.register(username, password, fullname, email):
            QMessageBox.information(self, "Cadastro realizado", "Usuário cadastrado com sucesso! Faça login para continuar.")
            self.auth_stack.setCurrentIndex(0)  # Volta para a tela de login
            
            # Limpa os campos
            self.reg_fullname_input.clear()
            self.reg_username_input.clear()
            self.reg_email_input.clear()
            self.reg_password_input.clear()
            self.reg_confirm_password_input.clear()
        else:
            QMessageBox.critical(self, "Erro no cadastro", "Nome de usuário ou e-mail já existente.")