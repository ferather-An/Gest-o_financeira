import sqlite3
import os
import datetime
import hashlib
import json
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_name="finance_manager.db"):
        # Cria o diretório de dados se não existir
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        self.db_path = data_dir / db_name
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Estabelece conexão com o banco de dados"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Para acessar colunas pelo nome
        self.cursor = self.connection.cursor()
        return self.connection
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
    
    def setup_database(self):
        """Configura o banco de dados com as tabelas necessárias"""
        conn = self.connect()
        
        # Tabela de usuários
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            settings TEXT
        )
        ''')
        
        # Tabela de categorias
        conn.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,  -- 'income' ou 'expense'
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Tabela de transações
        conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            category_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Inserir categorias padrão se não existirem
        self.insert_default_categories()
        
        conn.commit()
        self.close()
    
    def insert_default_categories(self):
        """Insere categorias padrão no banco de dados"""
        default_categories = [
            ("Salário", "income"),
            ("Renda Extra", "income"),
            ("Aluguel", "expense"),
            ("Alimentação", "expense"),
            ("Água", "expense"),
            ("Faculdade", "expense"),
            ("Seguro", "expense"),
            ("Gasolina", "expense"),
            ("Manutenção do carro", "expense"),
            ("Imposto", "expense")
        ]
        
        conn = self.connect()
        for name, type_ in default_categories:
            # Verifica se a categoria já existe
            self.cursor.execute("SELECT id FROM categories WHERE name = ? AND type = ?", (name, type_))
            if not self.cursor.fetchone():
                self.cursor.execute(
                    "INSERT INTO categories (name, type, user_id) VALUES (?, ?, NULL)",
                    (name, type_)
                )
        
        conn.commit()
        self.close()
    
    def register_user(self, username, password, full_name, email=None):
        """Registra um novo usuário no sistema"""
        try:
            conn = self.connect()
            
            # Hash da senha para armazenamento seguro
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Configurações padrão do usuário
            default_settings = {
                "theme": "light",
                "font_family": "Arial",
                "font_size": 10,
                "color_scheme": "default"
            }
            
            self.cursor.execute(
                "INSERT INTO users (username, password, full_name, email, settings) VALUES (?, ?, ?, ?, ?)",
                (username, hashed_password, full_name, email, json.dumps(default_settings))
            )
            
            user_id = self.cursor.lastrowid
            conn.commit()
            self.close()
            return user_id
        except sqlite3.IntegrityError:
            # Usuário já existe
            self.close()
            return None
    
    def authenticate_user(self, username, password):
        """Autentica um usuário"""
        conn = self.connect()
        
        # Hash da senha para comparação
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        self.cursor.execute(
            "SELECT id, username, full_name, settings FROM users WHERE username = ? AND password = ?",
            (username, hashed_password)
        )
        
        user = self.cursor.fetchone()
        self.close()
        
        if user:
            return {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "settings": json.loads(user["settings"])
            }
        return None
    
    def get_user_settings(self, user_id):
        """Obtém as configurações do usuário"""
        conn = self.connect()
        
        self.cursor.execute("SELECT settings FROM users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        
        self.close()
        
        if result:
            return json.loads(result["settings"])
        return None
    
    def update_user_settings(self, user_id, settings):
        """Atualiza as configurações do usuário"""
        conn = self.connect()
        
        self.cursor.execute(
            "UPDATE users SET settings = ? WHERE id = ?",
            (json.dumps(settings), user_id)
        )
        
        conn.commit()
        self.close()
    
    def add_transaction(self, user_id, date, amount, description, category_id):
        """Adiciona uma nova transação"""
        conn = self.connect()
        
        self.cursor.execute(
            "INSERT INTO transactions (date, amount, description, category_id, user_id) VALUES (?, ?, ?, ?, ?)",
            (date, amount, description, category_id, user_id)
        )
        
        transaction_id = self.cursor.lastrowid
        conn.commit()
        self.close()
        
        return transaction_id
    
    def get_transactions(self, user_id, start_date=None, end_date=None, category_id=None):
        """Obtém transações do usuário com filtros opcionais"""
        conn = self.connect()
        
        query = """
        SELECT t.id, t.date, t.amount, t.description, c.name as category_name, c.type as category_type
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        """
        
        params = [user_id]
        
        if start_date:
            query += " AND t.date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND t.date <= ?"
            params.append(end_date)
        
        if category_id:
            query += " AND t.category_id = ?"
            params.append(category_id)
        
        query += " ORDER BY t.date DESC"
        
        self.cursor.execute(query, params)
        transactions = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return transactions
    
    def get_categories(self, user_id=None, type_=None):
        """Obtém categorias com filtros opcionais"""
        conn = self.connect()
        
        query = "SELECT id, name, type FROM categories WHERE user_id IS NULL"
        params = []
        
        if user_id:
            query += " OR user_id = ?"
            params.append(user_id)
        
        if type_:
            query += " AND type = ?"
            params.append(type_)
        
        self.cursor.execute(query, params)
        categories = [dict(row) for row in self.cursor.fetchall()]
        
        self.close()
        return categories
    
    def get_balance(self, user_id, start_date=None, end_date=None):
        """Calcula o saldo atual do usuário"""
        conn = self.connect()
        
        query = """
        SELECT 
            SUM(CASE WHEN c.type = 'income' THEN t.amount ELSE 0 END) as total_income,
            SUM(CASE WHEN c.type = 'expense' THEN t.amount ELSE 0 END) as total_expense
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        """
        
        params = [user_id]
        
        if start_date:
            query += " AND t.date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND t.date <= ?"
            params.append(end_date)
        
        self.cursor.execute(query, params)
        result = self.cursor.fetchone()
        
        self.close()
        
        if result:
            total_income = result["total_income"] or 0
            total_expense = result["total_expense"] or 0
            return total_income - total_expense
        
        return 0
    
    def get_monthly_summary(self, user_id, year, month):
        """Obtém o resumo mensal de receitas e despesas"""
        conn = self.connect()
        
        # Formata as datas para o mês específico
        start_date = f"{year}-{month:02d}-01"
        
        # Determina o último dia do mês
        if month == 12:
            next_month_year = year + 1
            next_month = 1
        else:
            next_month_year = year
            next_month = month + 1
        
        end_date = f"{next_month_year}-{next_month:02d}-01"
        
        # Consulta para obter receitas por categoria
        income_query = """
        SELECT c.name, SUM(t.amount) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND c.type = 'income'
        AND t.date >= ? AND t.date < ?
        GROUP BY c.name
        ORDER BY total DESC
        """
        
        # Consulta para obter despesas por categoria
        expense_query = """
        SELECT c.name, SUM(t.amount) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND c.type = 'expense'
        AND t.date >= ? AND t.date < ?
        GROUP BY c.name
        ORDER BY total DESC
        """
        
        self.cursor.execute(income_query, (user_id, start_date, end_date))
        income_categories = [dict(row) for row in self.cursor.fetchall()]
        
        self.cursor.execute(expense_query, (user_id, start_date, end_date))
        expense_categories = [dict(row) for row in self.cursor.fetchall()]
        
        # Calcula totais
        total_income = sum(item["total"] for item in income_categories)
        total_expense = sum(item["total"] for item in expense_categories)
        
        self.close()
        
        return {
            "income": {
                "categories": income_categories,
                "total": total_income
            },
            "expense": {
                "categories": expense_categories,
                "total": total_expense
            },
            "balance": total_income - total_expense
        }
    
    def backup_data(self, backup_path):
        """Cria um backup do banco de dados"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Erro ao criar backup: {e}")
            return False
    
    def restore_backup(self, backup_path):
        """Restaura um backup do banco de dados"""
        try:
            self.close()  # Fecha qualquer conexão existente
            import shutil
            shutil.copy2(backup_path, self.db_path)
            return True
        except Exception as e:
            print(f"Erro ao restaurar backup: {e}")
            return False
    
    def export_to_csv(self, user_id, file_path, start_date=None, end_date=None):
        """Exporta transações para CSV"""
        import csv
        
        transactions = self.get_transactions(user_id, start_date, end_date)
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['date', 'category_name', 'description', 'amount', 'category_type']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for transaction in transactions:
                    writer.writerow({
                        'date': transaction['date'],
                        'category_name': transaction['category_name'],
                        'description': transaction['description'],
                        'amount': transaction['amount'],
                        'category_type': transaction['category_type']
                    })
            
            return True
        except Exception as e:
            print(f"Erro ao exportar para CSV: {e}")
            return False
    
    def import_from_csv(self, user_id, file_path):
        """Importa transações de um arquivo CSV"""
        import csv
        
        try:
            conn = self.connect()
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Busca o ID da categoria pelo nome
                    self.cursor.execute(
                        "SELECT id FROM categories WHERE name = ? AND type = ?",
                        (row['category_name'], row['category_type'])
                    )
                    
                    category = self.cursor.fetchone()
                    if not category:
                        # Cria a categoria se não existir
                        self.cursor.execute(
                            "INSERT INTO categories (name, type, user_id) VALUES (?, ?, ?)",
                            (row['category_name'], row['category_type'], user_id)
                        )
                        category_id = self.cursor.lastrowid
                    else:
                        category_id = category['id']
                    
                    # Insere a transação
                    self.cursor.execute(
                        "INSERT INTO transactions (date, amount, description, category_id, user_id) VALUES (?, ?, ?, ?, ?)",
                        (row['date'], float(row['amount']), row['description'], category_id, user_id)
                    )
            
            conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"Erro ao importar do CSV: {e}")
            self.close()
            return False