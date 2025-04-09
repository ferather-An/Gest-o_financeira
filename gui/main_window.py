from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTabWidget, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QComboBox, QDateEdit,
                            QLineEdit, QFormLayout, QDialog, QMessageBox,
                            QFileDialog, QCheckBox, QGroupBox, QStackedWidget,
                            QSplitter, QFrame, QToolButton, QMenu, QAction,
                            QSpinBox, QDoubleSpinBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QDate, QDateTime, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from backend.finance_manager import FinanceManager
import datetime
import calendar
import os

class MainWindow(QMainWindow):
    def __init__(self, auth_manager):
        super().__init__()
        
        self.auth_manager = auth_manager
        self.user = auth_manager.get_current_user()
        
        # Inicializa o gerenciador financeiro
        self.finance_manager = FinanceManager(self.user["id"])
        
        # Configurações de tema
        self.theme = self.user["settings"]["theme"]
        self.font_family = self.user["settings"]["font_family"]
        self.font_size = self.user["settings"]["font_size"]
        self.color_scheme = self.user["settings"]["color_scheme"]
        
        # Configura a janela
        self.setWindowTitle("Sistema de Gestão Financeira")
        self.setMinimumSize(1200, 800)
        
        # Cria a interface
        self.setup_ui()
        
        # Aplica o tema
        self.apply_theme()
        
        # Carrega os dados iniciais
        self.load_data()
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barra superior
        top_bar = QWidget()
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 10, 20, 10)
        
        # Informações do usuário
        user_info = QLabel(f"Bem-vindo, {self.user['full_name']}!")
        user_info.setFont(QFont(self.font_family, 12, QFont.Bold))
        
        # Menu de configurações
        settings_button = QToolButton()
        settings_button.setIcon(QIcon.fromTheme("preferences-system"))
        settings_button.setIconSize(QSize(24, 24))
        settings_button.setCursor(Qt.PointingHandCursor)
        
        settings_menu = QMenu()
        
        theme_action = QAction("Alterar Tema", self)
        theme_action.triggered.connect(self.show_theme_dialog)
        
        logout_action = QAction("Sair", self)
        logout_action.triggered.connect(self.logout)
        
        settings_menu.addAction(theme_action)
        settings_menu.addSeparator()
        settings_menu.addAction(logout_action)
        
        settings_button.setMenu(settings_menu)
        settings_button.setPopupMode(QToolButton.InstantPopup)
        
        top_bar_layout.addWidget(user_info)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(settings_button)
        
        # Barra de navegação
        nav_bar = QWidget()
        nav_bar_layout = QHBoxLayout(nav_bar)
        nav_bar_layout.setContentsMargins(20, 10, 20, 10)
        
        # Botões de navegação
        self.nav_buttons = {}
        
        for text, page_index in [
            ("Lançamentos", 0),
            ("Relatórios", 1),
            ("Importar", 2),
            ("Exportar", 3),
            ("Análise", 4)
        ]:
            button = QPushButton(text)
            button.setCheckable(True)
            button.setMinimumHeight(40)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda checked, idx=page_index: self.content_stack.setCurrentIndex(idx))
            
            nav_bar_layout.addWidget(button)
            self.nav_buttons[page_index] = button
        
        # Marca o primeiro botão como selecionado
        self.nav_buttons[0].setChecked(True)
        
        # Conteúdo principal
        self.content_stack = QStackedWidget()
        
        # Página de lançamentos
        self.setup_transactions_page()
        
        # Página de relatórios
        self.setup_reports_page()
        
        # Página de importação
        self.setup_import_page()
        
        # Página de exportação
        self.setup_export_page()
        
        # Página de análise
        self.setup_analysis_page()
        
        # Barra de status
        status_bar = QWidget()
        status_bar_layout = QHBoxLayout(status_bar)
        status_bar_layout.setContentsMargins(20, 10, 20, 10)
        
        # Saldo atual
        self.balance_label = QLabel()
        self.balance_label.setFont(QFont(self.font_family, 12, QFont.Bold))
        
        # Desenvolvedor
        developer_label = QLabel("Desenvolvido por Icaro Feldmann")
        developer_label.setAlignment(Qt.AlignRight)
        
        status_bar_layout.addWidget(self.balance_label)
        status_bar_layout.addStretch()
        status_bar_layout.addWidget(developer_label)
        
        # Adiciona os widgets ao layout principal
        main_layout.addWidget(top_bar)
        main_layout.addWidget(nav_bar)
        main_layout.addWidget(self.content_stack, 1)
        main_layout.addWidget(status_bar)
    
    def setup_transactions_page(self):
        """Configura a página de lançamentos"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        # Saldo atual
        self.transactions_balance_label = QLabel()
        self.transactions_balance_label.setFont(QFont(self.font_family, 14, QFont.Bold))
        
        # Botões de ação
        action_layout = QHBoxLayout()
        
        add_button = QPushButton("Lançar")
        add_button.setMinimumHeight(40)
        add_button.clicked.connect(self.show_add_transaction_dialog)
        
        edit_button = QPushButton("Editar")
        edit_button.setMinimumHeight(40)
        edit_button.clicked.connect(self.edit_selected_transaction)
        
        delete_button = QPushButton("Excluir")
        delete_button.setMinimumHeight(40)
        delete_button.clicked.connect(self.delete_selected_transaction)
        
        action_layout.addWidget(add_button)
        action_layout.addWidget(edit_button)
        action_layout.addWidget(delete_button)
        
        # Botões de zoom
        zoom_layout = QHBoxLayout()
        
        zoom_in_button = QPushButton("+")
        zoom_in_button.setFixedSize(40, 40)
        zoom_in_button.clicked.connect(lambda: self.change_font_size(1))
        
        zoom_out_button = QPushButton("-")
        zoom_out_button.setFixedSize(40, 40)
        zoom_out_button.clicked.connect(lambda: self.change_font_size(-1))
        
        zoom_layout.addWidget(zoom_in_button)
        zoom_layout.addWidget(zoom_out_button)
        
        header_layout.addWidget(self.transactions_balance_label)
        header_layout.addStretch()
        header_layout.addLayout(action_layout)
        header_layout.addLayout(zoom_layout)
        
        # Barra lateral de busca
        sidebar_layout = QVBoxLayout()
        
        search_group = QGroupBox("Buscas")
        search_layout = QVBoxLayout(search_group)
        
        # Botões de busca
        search_buttons = [
            "Todos Lançamentos",
            "Mês",
            "Data",
            "Período",
            "Categoria",
            "Descrição",
            "Receitas",
            "Despesas",
            "Intervalo de Receitas",
            "Intervalo de Despesas"
        ]
        
        for text in search_buttons:
            button = QPushButton(text)
            button.setMinimumHeight(40)
            search_layout.addWidget(button)
        
        # Grupo de funções
        functions_group = QGroupBox("Funções")
        functions_layout = QVBoxLayout(functions_group)
        
        function_buttons = [
            "Imprimir",
            "Salvar PDF",
            "Exportar Backup",
            "Importar Backup"
        ]
        
        for text in function_buttons:
            button = QPushButton(text)
            button.setMinimumHeight(40)
            functions_layout.addWidget(button)
        
        sidebar_layout.addWidget(search_group)
        sidebar_layout.addWidget(functions_group)
        sidebar_layout.addStretch()
        
        # Tabela de transações
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels(["Data", "Categoria", "Descrição", "Movimentação", "Acumulado", ""])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transactions_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.transactions_table.setColumnWidth(5, 30)
        self.transactions_table.verticalHeader().setVisible(False)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transactions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Layout da página
        content_layout = QHBoxLayout()
        content_layout.addLayout(sidebar_layout)
        content_layout.addWidget(self.transactions_table, 3)
        
        # Botão de selecionar tudo
        select_all_button = QPushButton("Selecionar Tudo")
        select_all_button.setMinimumHeight(40)
        select_all_button.clicked.connect(self.select_all_transactions)
        
        layout.addLayout(header_layout)
        layout.addLayout(content_layout)
        layout.addWidget(select_all_button, alignment=Qt.AlignCenter)
        
        self.content_stack.addWidget(page)
    
    def setup_reports_page(self):
        """Configura a página de relatórios"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        # Título
        title_label = QLabel("Relatórios")
        title_label.setFont(QFont(self.font_family, 16, QFont.Bold))
        
        # Botões de ação
        action_layout = QHBoxLayout()
        
        report_button = QPushButton("Relatório")
        report_button.setMinimumHeight(40)
        report_button.clicked.connect(self.generate_report)
        
        print_button = QPushButton("Imprimir")
        print_button.setMinimumHeight(40)
        print_button.clicked.connect(self.print_report)
        
        pdf_button = QPushButton("Baixar PDF")
        pdf_button.setMinimumHeight(40)
        pdf_button.clicked.connect(self.save_report_pdf)
        
        action_layout.addWidget(report_button)
        action_layout.addWidget(print_button)
        action_layout.addWidget(pdf_button)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(action_layout)
        
        # Área de visualização do relatório
        self.report_view = QLabel()
        self.report_view.setAlignment(Qt.AlignCenter)
        self.report_view.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.report_view.setMinimumHeight(500)
        
        # Configurações do relatório
        config_layout = QHBoxLayout()
        
        # Tipo de relatório
        report_type_layout = QVBoxLayout()
        report_type_label = QLabel("Tipo de Relatório:")
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["Fluxo de Caixa", "Resultado"])
        self.report_type_combo.setMinimumHeight(40)
        
        report_type_layout.addWidget(report_type_label)
        report_type_layout.addWidget(self.report_type_combo)
        
        # Período
        period_layout = QVBoxLayout()
        period_label = QLabel("Período:")
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Mensal", "Anual", "Personalizado"])
        self.period_combo.setMinimumHeight(40)
        
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.period_combo)
        
        # Ano
        year_layout = QVBoxLayout()
        year_label = QLabel("Ano:")
        self.year_input = QLineEdit()
        self.year_input.setText(str(datetime.date.today().year))
        self.year_input.setMinimumHeight(40)
        
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_input)
        
        config_layout.addLayout(report_type_layout)
        config_layout.addLayout(period_layout)
        config_layout.addLayout(year_layout)
        
        # Botões de ação
        action_buttons_layout = QHBoxLayout()
        
        generate_button = QPushButton("Gerar Relatório")
        generate_button.setMinimumHeight(40)
        generate_button.clicked.connect(self.generate_report)
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.setMinimumHeight(40)
        
        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(generate_button)
        action_buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.report_view, 1)
        layout.addLayout(config_layout)
        layout.addLayout(action_buttons_layout)
        
        self.content_stack.addWidget(page)
    
    def setup_import_page(self):
        """Configura a página de importação"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        # Título
        title_label = QLabel("Importação CSV")
        title_label.setFont(QFont(self.font_family, 16, QFont.Bold))
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Área de visualização da importação
        self.import_table = QTableWidget()
        self.import_table.setColumnCount(4)
        self.import_table.setHorizontalHeaderLabels(["Data", "Categoria", "Descrição", "Movimento"])
        self.import_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.import_table.verticalHeader().setVisible(False)
        self.import_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.import_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.import_table.setMinimumHeight(400)
        
        # Botões de ação
        action_buttons_layout = QHBoxLayout()
        
        import_button = QPushButton("Importar")
        import_button.setMinimumHeight(40)
        import_button.clicked.connect(self.import_csv)
        
        back_button = QPushButton("Voltar")
        back_button.setMinimumHeight(40)
        
        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(import_button)
        action_buttons_layout.addWidget(back_button)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.import_table, 1)
        layout.addLayout(action_buttons_layout)
        
        self.content_stack.addWidget(page)
    
    def setup_export_page(self):
        """Configura a página de exportação"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        # Título
        title_label = QLabel("Exportação")
        title_label.setFont(QFont(self.font_family, 16, QFont.Bold))
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Opções de exportação
        options_group = QGroupBox("Opções de Exportação")
        options_layout = QVBoxLayout(options_group)
        
        # Formato
        format_layout = QHBoxLayout()
        format_label = QLabel("Formato:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "PDF"])
        self.format_combo.setMinimumHeight(40)
        
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        
        # Período
        period_layout = QHBoxLayout()
        period_label = QLabel("Período:")
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        self.start_date.setMinimumHeight(40)
        
        period_to_label = QLabel("até")
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setMinimumHeight(40)
        
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.start_date)
        period_layout.addWidget(period_to_label)
        period_layout.addWidget(self.end_date)
        
        options_layout.addLayout(format_layout)
        options_layout.addLayout(period_layout)
        
        # Botões de ação
        action_buttons_layout = QHBoxLayout()
        
        export_button = QPushButton("Exportar")
        export_button.setMinimumHeight(40)
        export_button.clicked.connect(self.export_data)
        
        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(export_button)
        
        layout.addLayout(header_layout)
        layout.addWidget(options_group)
        layout.addStretch()
        layout.addLayout(action_buttons_layout)
        
        self.content_stack.addWidget(page)
    
    def setup_analysis_page(self):
        """Configura a página de análise"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        # Botões de ação
        filter_button = QPushButton("Filtrar")
        filter_button.setMinimumHeight(40)
        filter_button.clicked.connect(self.show_filter_dialog)
        
        style_button = QPushButton("Alterar Estilo")
        style_button.setMinimumHeight(40)
        style_button.clicked.connect(self.show_style_dialog)
        
        header_layout.addWidget(filter_button)
        header_layout.addWidget(style_button)
        header_layout.addStretch()
        
        # Gráficos
        charts_layout = QGridLayout()
        
        # Gráfico de desempenho
        self.performance_chart = QLabel()
        self.performance_chart.setAlignment(Qt.AlignCenter)
        self.performance_chart.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.performance_chart.setMinimumHeight(300)
        
        # Gráfico de movimentação
        self.movement_chart = QLabel()
        self.movement_chart.setAlignment(Qt.AlignCenter)
        self.movement_chart.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.movement_chart.setMinimumHeight(300)
        
        # Gráfico de categorias de receita
        self.income_chart = QLabel()
        self.income_chart.setAlignment(Qt.AlignCenter)
        self.income_chart.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.income_chart.setMinimumHeight(300)
        
        # Gráfico de categorias de despesa
        self.expense_chart = QLabel()
        self.expense_chart.setAlignment(Qt.AlignCenter)
        self.expense_chart.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.expense_chart.setMinimumHeight(300)
        
        charts_layout.addWidget(self.performance_chart, 0, 0)
        charts_layout.addWidget(self.income_chart, 0, 1)
        charts_layout.addWidget(self.movement_chart, 1, 0)
        charts_layout.addWidget(self.expense_chart, 1, 1)
        
        # Painel de análise
        analysis_group = QGroupBox("Análise")
        analysis_layout = QVBoxLayout(analysis_group)
        
        # Período
        period_layout = QHBoxLayout()
        
        period_label = QLabel("Período:")
        self.analysis_period_combo = QComboBox()
        self.analysis_period_combo.addItems(["Mensal", "Anual"])
        self.analysis_period_combo.setMinimumHeight(40)
        
        month_label = QLabel("Mês:")
        self.analysis_month_combo = QComboBox()
        self.analysis_month_combo.addItems([calendar.month_name[i] for i in range(1, 13)])
        self.analysis_month_combo.setCurrentIndex(datetime.date.today().month - 1)
        self.analysis_month_combo.setMinimumHeight(40)
        
        year_label = QLabel("Ano:")
        self.analysis_year_input = QLineEdit()
        self.analysis_year_input.setText(str(datetime.date.today().year))
        self.analysis_year_input.setMinimumHeight(40)
        
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.analysis_period_combo)
        period_layout.addWidget(month_label)
        period_layout.addWidget(self.analysis_month_combo)
        period_layout.addWidget(year_label)
        period_layout.addWidget(self.analysis_year_input)
        
        # Botões de ação
        action_buttons_layout = QHBoxLayout()
        
        analyze_button = QPushButton("Analisar")
        analyze_button.setMinimumHeight(40)
        analyze_button.clicked.connect(self.analyze_data)
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.setMinimumHeight(40)
        
        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(analyze_button)
        action_buttons_layout.addWidget(cancel_button)
        
        analysis_layout.addLayout(period_layout)
        analysis_layout.addLayout(action_buttons_layout)
        
        layout.addLayout(header_layout)
        layout.addLayout(charts_layout)
        layout.addWidget(analysis_group)
        
        self.content_stack.addWidget(page)
    
    def apply_theme(self):
        """Aplica o tema atual à interface"""
        if self.theme == "dark":
            self.setStyleSheet(f"""
                QMainWindow, QWidget {{
                    background-color: #2D2D2D;
                    color: white;
                    font-family: {self.font_family};
                    font-size: {self.font_size}pt;
                }}
                QLabel {{
                    color: white;
                }}
                QPushButton {{
                    background-color: #9370DB;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #8A2BE2;
                }}
                QPushButton:checked {{
                    background-color: #8A2BE2;
                }}
                QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {{
                    background-color: #3D3D3D;
                    color: white;
                    border: 1px solid #5D5D5D;
                    border-radius: 5px;
                    padding: 5px;
                }}
                QTableWidget {{
                    background-color: #3D3D3D;
                    color: white;
                    gridline-color: #5D5D5D;
                }}
                QTableWidget::item {{
                    padding: 5px;
                }}
                QTableWidget::item:selected {{
                    background-color: #9370DB;
                }}
                QHeaderView::section {{
                    background-color: #2D2D2D;
                    color: white;
                    padding: 5px;
                    border: 1px solid #5D5D5D;
                }}
                QGroupBox {{
                    border: 1px solid #5D5D5D;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 5px;
                }}
            """)
        else:  # light
            self.setStyleSheet(f"""
                QMainWindow, QWidget {{
                    background-color: white;
                    color: black;
                    font-family: {self.font_family};
                    font-size: {self.font_size}pt;
                }}
                QLabel {{
                    color: black;
                }}
                QPushButton {{
                    background-color: #9370DB;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #8A2BE2;
                }}
                QPushButton:checked {{
                    background-color: #8A2BE2;
                }}
                QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {{
                    background-color: white;
                    color: black;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 5px;
                }}
                QTableWidget {{
                    background-color: white;
                    color: black;
                    gridline-color: #ccc;
                }}
                QTableWidget::item {{
                    padding: 5px;
                }}
                QTableWidget::item:selected {{
                    background-color: #9370DB;
                    color: white;
                }}
                QHeaderView::section {{
                    background-color: #f0f0f0;
                    color: black;
                    padding: 5px;
                    border: 1px solid #ccc;
                }}
                QGroupBox {{
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 5px;
                }}
            """)
        
        # Atualiza a interface
        self.update()
    
    def load_data(self):
        """Carrega os dados iniciais"""
        # Atualiza o saldo
        self.update_balance()
        
        # Carrega as transações
        self.load_transactions()
        
        # Gera os gráficos iniciais
        self.analyze_data()
    
    def update_balance(self):
        """Atualiza o saldo exibido"""
        balance = self.finance_manager.get_balance()
        
        # Formata o saldo
        balance_text = f"Saldo Atual: R$ {balance:.2f}"
        
        # Define a cor com base no saldo
        if balance >= 0:
            balance_color = "green"
        else:
            balance_color = "red"
        
        # Atualiza os labels
        self.balance_label.setText(balance_text)
        self.balance_label.setStyleSheet(f"color: {balance_color};")
        
        self.transactions_balance_label.setText(balance_text)
        self.transactions_balance_label.setStyleSheet(f"color: {balance_color};")
    
    def load_transactions(self):
        """Carrega as transações na tabela"""
        # Obtém as transações
        transactions = self.finance_manager.get_transactions()
        
        # Limpa a tabela
        self.transactions_table.setRowCount(0)
        
        # Preenche a tabela
        accumulated = 0
        for i, transaction in enumerate(transactions):
            self.transactions_table.insertRow(i)
            
            # Data
            date_item = QTableWidgetItem(transaction["date"])
            self.transactions_table.setItem(i, 0, date_item)
            
            # Categoria
            category_item = QTableWidgetItem(transaction["category_name"])
            self.transactions_table.setItem(i, 1, category_item)
            
            # Descrição
            description_item = QTableWidgetItem(transaction["description"])
            self.transactions_table.setItem(i, 2, description_item)
            
            # Movimentação
            amount = transaction["amount"]
            if transaction["category_type"] == "expense":
                amount = -amount
                amount_text = f"-{amount:.2f}"
                amount_color = "red"
            else:
                amount_text = f"{amount:.2f}"
                amount_color = "green"
            
            amount_item = QTableWidgetItem(amount_text)
            amount_item.setForeground(QColor(amount_color))
            self.transactions_table.setItem(i, 3, amount_item)
            
            # Acumulado
            accumulated += amount
            accumulated_item = QTableWidgetItem(f"{accumulated:.2f}")
            self.transactions_table.setItem(i, 4, accumulated_item)
            
            # Checkbox
            checkbox = QTableWidgetItem()
            checkbox.setCheckState(Qt.Unchecked)
            self.transactions_table.setItem(i, 5, checkbox)
    
    def show_add_transaction_dialog(self):
        """Exibe o diálogo para adicionar uma nova transação"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Cadastro")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Tipo de transação
        type_layout = QHBoxLayout()
        
        income_radio = QRadioButton("Receita")
        income_radio.setChecked(True)
        
        expense_radio = QRadioButton("Despesa")
        
        type_group = QButtonGroup()
        type_group.addButton(income_radio, 1)
        type_group.addButton(expense_radio, 2)
        
        type_layout.addWidget(income_radio)
        type_layout.addWidget(expense_radio)
        
        # Valor
        amount_layout = QHBoxLayout()
        amount_label = QLabel("Valor:")
        amount_input = QDoubleSpinBox()
        amount_input.setRange(0, 1000000)
        amount_input.setDecimals(2)
        amount_input.setSingleStep(10)
        amount_input.setValue(0)
        amount_input.setMinimumHeight(40)
        
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(amount_input)
        
        # Data
        date_layout = QHBoxLayout()
        date_label = QLabel("Data:")
        date_input = QDateEdit()
        date_input.setDate(QDate.currentDate())
        date_input.setCalendarPopup(True)
        date_input.setMinimumHeight(40)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(date_input)
        
        # Categoria
        category_layout = QHBoxLayout()
        category_label = QLabel("Categoria:")
        category_combo = QComboBox()
        
        # Carrega as categorias de receita por padrão
        income_categories = self.finance_manager.get_categories("income")
        for category in income_categories:
            category_combo.addItem(category["name"], category["id"])
        
        category_combo.setMinimumHeight(40)
        
        add_category_button = QPushButton("+")
        add_category_button.setFixedSize(40, 40)
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(category_combo)
        category_layout.addWidget(add_category_button)
        
        # Atualiza as categorias quando o tipo muda
        def update_categories():
            category_combo.clear()
            
            if income_radio.isChecked():
                categories = self.finance_manager.get_categories("income")
            else:
                categories = self.finance_manager.get_categories("expense")
            
            for category in categories:
                category_combo.addItem(category["name"], category["id"])
        
        income_radio.toggled.connect(update_categories)
        
        # Descrição
        description_layout = QVBoxLayout()
        description_label = QLabel("Descrição:")
        description_input = QLineEdit()
        description_input.setPlaceholderText("Descrição da transação")
        description_input.setMinimumHeight(40)
        
        description_layout.addWidget(description_label)
        description_layout.addWidget(description_input)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Salvar")
        save_button.setMinimumHeight(40)
        
        clear_button = QPushButton("Limpar")
        clear_button.setMinimumHeight(40)
        clear_button.clicked.connect(lambda: description_input.clear())
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(clear_button)
        
        # Adiciona os layouts ao layout principal
        layout.addLayout(type_layout)
        layout.addLayout(amount_layout)
        layout.addLayout(date_layout)
        layout.addLayout(category_layout)
        layout.addLayout(description_layout)
        layout.addLayout(buttons_layout)
        
        # Função para salvar a transação
        def save_transaction():
            try:
                # Obtém os valores
                transaction_type = "income" if income_radio.isChecked() else "expense"
                amount = amount_input.value()
                date = date_input.date().toString("yyyy-MM-dd")
                category_id = category_combo.currentData()
                description = description_input.text()
                
                # Valida os dados
                if amount <= 0:
                    QMessageBox.warning(dialog, "Valor inválido", "O valor deve ser maior que zero.")
                    return
                
                if not description:
                    QMessageBox.warning(dialog, "Descrição vazia", "Por favor, forneça uma descrição.")
                    return
                
                # Adiciona a transação
                self.finance_manager.add_transaction(date, amount, description, category_id)
                
                # Atualiza a interface
                self.update_balance()
                self.load_transactions()
                
                # Fecha o diálogo
                dialog.accept()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Erro", f"Ocorreu um erro: {str(e)}")
        
        save_button.clicked.connect(save_transaction)
        
        dialog.exec_()
    
    def edit_selected_transaction(self):
        """Edita a transação selecionada"""
        # Verifica se há uma linha selecionada
        selected_rows = []
        for i in range(self.transactions_table.rowCount()):
            if self.transactions_table.item(i, 5).checkState() == Qt.Checked:
                selected_rows.append(i)
        
        if not selected_rows:
            QMessageBox.warning(self, "Nenhuma seleção", "Por favor, selecione uma transação para editar.")
            return
        
        if len(selected_rows) > 1:
            QMessageBox.warning(self, "Múltiplas seleções", "Por favor, selecione apenas uma transação para editar.")
            return
        
        # Implementação da edição (simplificada)
        QMessageBox.information(self, "Editar", "Funcionalidade de edição a ser implementada.")
    
    def delete_selected_transaction(self):
        """Exclui as transações selecionadas"""
        # Verifica se há linhas selecionadas
        selected_rows = []
        for i in range(self.transactions_table.rowCount()):
            if self.transactions_table.item(i, 5).checkState() == Qt.Checked:
                selected_rows.append(i)
        
        if not selected_rows:
            QMessageBox.warning(self, "Nenhuma seleção", "Por favor, selecione pelo menos uma transação para excluir.")
            return
        
        # Confirmação
        confirm = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f"Tem certeza que deseja excluir {len(selected_rows)} transação(ões)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Implementação da exclusão (simplificada)
            QMessageBox.information(self, "Excluir", "Funcionalidade de exclusão a ser implementada.")
    
    def select_all_transactions(self):
        """Seleciona todas as transações"""
        for i in range(self.transactions_table.rowCount()):
            self.transactions_table.item(i, 5).setCheckState(Qt.Checked)
    
    def generate_report(self):
        """Gera um relatório"""
        # Implementação simplificada
        report_type = self.report_type_combo.currentText()
        period = self.period_combo.currentText()
        year = int(self.year_input.text())
        
        # Exibe uma mensagem de exemplo
        self.report_view.setText(f"Relatório de {report_type} - {period} de {year}")
    
    def print_report(self):
        """Imprime o relatório atual"""
        # Implementação simplificada
        QMessageBox.information(self, "Imprimir", "Funcionalidade de impressão a ser implementada.")
    
    def save_report_pdf(self):
        """Salva o relatório como PDF"""
        # Implementação simplificada
        QMessageBox.information(self, "Salvar PDF", "Funcionalidade de salvar PDF a ser implementada.")
    
    def import_csv(self):
        """Importa dados de um arquivo CSV"""
        # Abre o diálogo de seleção de arquivo
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo CSV",
            "",
            "Arquivos CSV (*.csv)"
        )
        
        if file_path:
            # Implementação simplificada
            QMessageBox.information(self, "Importar CSV", f"Arquivo selecionado: {file_path}")
    
    def export_data(self):
        """Exporta dados para um arquivo"""
        format_type = self.format_combo.currentText()
        
        # Abre o diálogo de salvamento de arquivo
        if format_type == "CSV":
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar arquivo CSV",
                "",
                "Arquivos CSV (*.csv)"
            )
        else:  # PDF
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar arquivo PDF",
                "",
                "Arquivos PDF (*.pdf)"
            )
        
        if file_path:
            # Implementação simplificada
            QMessageBox.information(self, "Exportar", f"Arquivo salvo: {file_path}")
    
    def show_filter_dialog(self):
        """Exibe o diálogo de filtro para análise"""
        # Implementação simplificada
        QMessageBox.information(self, "Filtrar", "Funcionalidade de filtro a ser implementada.")
    
    def show_style_dialog(self):
        """Exibe o diálogo de estilo para análise"""
        # Implementação simplificada
        QMessageBox.information(self, "Alterar Estilo", "Funcionalidade de alteração de estilo a ser implementada.")
    
    def analyze_data(self):
        """Analisa os dados e gera os gráficos"""
        try:
            # Obtém o período selecionado
            year = int(self.analysis_year_input.text())
            month = self.analysis_month_combo.currentIndex() + 1
            
            # Gera os gráficos
            performance_pixmap = self.finance_manager.generate_performance_chart(year, month, self.theme)
            if performance_pixmap:
                self.performance_chart.setPixmap(performance_pixmap)
            
            movement_pixmap = self.finance_manager.generate_movement_chart(year, month, self.theme)
            if movement_pixmap:
                self.movement_chart.setPixmap(movement_pixmap)
            
            income_pixmap, expense_pixmap = self.finance_manager.generate_category_charts(year, month, self.theme)
            if income_pixmap:
                self.income_chart.setPixmap(income_pixmap)
            if expense_pixmap:
                self.expense_chart.setPixmap(expense_pixmap)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar gráficos: {str(e)}")
    
    def show_theme_dialog(self):
        """Exibe o diálogo de configuração de tema"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Configurações de Tema")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Tema
        theme_group = QGroupBox("Tema")
        theme_layout = QVBoxLayout(theme_group)
        
        light_radio = QRadioButton("Claro")
        light_radio.setChecked(self.theme == "light")
        
        dark_radio = QRadioButton("Escuro")
        dark_radio.setChecked(self.theme == "dark")
        
        theme_layout.addWidget(light_radio)
        theme_layout.addWidget(dark_radio)
        
        # Fonte
        font_group = QGroupBox("Fonte")
        font_layout = QVBoxLayout(font_group)
        
        font_family_layout = QHBoxLayout()
        font_family_label = QLabel("Família:")
        font_family_combo = QComboBox()
        font_family_combo.addItems(["Arial", "Helvetica", "Times New Roman", "Courier New"])
        font_family_combo.setCurrentText(self.font_family)
        
        font_family_layout.addWidget(font_family_label)
        font_family_layout.addWidget(font_family_combo)
        
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Tamanho:")
        font_size_spin = QSpinBox()
        font_size_spin.setRange(8, 16)
        font_size_spin.setValue(self.font_size)
        
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(font_size_spin)
        
        font_layout.addLayout(font_family_layout)
        font_layout.addLayout(font_size_layout)
        
        # Esquema de cores
        color_group = QGroupBox("Esquema de Cores")
        color_layout = QVBoxLayout(color_group)
        
        color_combo = QComboBox()
        color_combo.addItems(["Padrão", "Azul", "Verde", "Vermelho"])
        color_combo.setCurrentText(self.color_scheme.capitalize())
        
        color_layout.addWidget(color_combo)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Salvar")
        save_button.clicked.connect(lambda: self.save_theme_settings(
            "light" if light_radio.isChecked() else "