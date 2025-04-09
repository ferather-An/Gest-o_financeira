from database.db_manager import DatabaseManager
import datetime
import calendar
import matplotlib.pyplot as plt
import io
import numpy as np
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QByteArray, QBuffer

class FinanceManager:
    def __init__(self, user_id=None):
        self.db_manager = DatabaseManager()
        self.user_id = user_id
    
    def set_user(self, user_id):
        """Define o usuário atual"""
        self.user_id = user_id
    
    def add_transaction(self, date, amount, description, category_id):
        """Adiciona uma nova transação"""
        if not self.user_id:
            return False
        
        return self.db_manager.add_transaction(
            self.user_id, date, amount, description, category_id
        )
    
    def get_transactions(self, start_date=None, end_date=None, category_id=None):
        """Obtém transações do usuário"""
        if not self.user_id:
            return []
        
        return self.db_manager.get_transactions(
            self.user_id, start_date, end_date, category_id
        )
    
    def get_categories(self, type_=None):
        """Obtém categorias disponíveis"""
        return self.db_manager.get_categories(self.user_id, type_)
    
    def get_balance(self, start_date=None, end_date=None):
        """Obtém o saldo atual"""
        if not self.user_id:
            return 0
        
        return self.db_manager.get_balance(self.user_id, start_date, end_date)
    
    def get_monthly_summary(self, year=None, month=None):
        """Obtém o resumo mensal"""
        if not self.user_id:
            return None
        
        if year is None or month is None:
            today = datetime.date.today()
            year = today.year
            month = today.month
        
        return self.db_manager.get_monthly_summary(self.user_id, year, month)
    
    def export_to_csv(self, file_path, start_date=None, end_date=None):
        """Exporta transações para CSV"""
        if not self.user_id:
            return False
        
        return self.db_manager.export_to_csv(self.user_id, file_path, start_date, end_date)
    
    def import_from_csv(self, file_path):
        """Importa transações de CSV"""
        if not self.user_id:
            return False
        
        return self.db_manager.import_from_csv(self.user_id, file_path)
    
    def backup_data(self, backup_path):
        """Cria um backup do banco de dados"""
        return self.db_manager.backup_data(backup_path)
    
    def restore_backup(self, backup_path):
        """Restaura um backup do banco de dados"""
        return self.db_manager.restore_backup(backup_path)
    
    def generate_performance_chart(self, year, month, theme="light"):
        """Gera um gráfico de desempenho diário"""
        if not self.user_id:
            return None
        
        # Configura cores baseadas no tema
        if theme == "dark":
            plt.style.use('dark_background')
            line_color = '#9370DB'  # Roxo claro
            fill_color = '#9370DB'
            text_color = 'white'
        else:
            plt.style.use('default')
            line_color = '#9370DB'  # Roxo
            fill_color = '#9370DB'
            text_color = 'black'
        
        # Obtém o número de dias no mês
        _, num_days = calendar.monthrange(year, month)
        
        # Prepara as datas para o mês
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{num_days:02d}"
        
        # Obtém as transações do mês
        transactions = self.get_transactions(start_date, end_date)
        
        # Organiza as transações por dia
        daily_balance = {}
        for day in range(1, num_days + 1):
            daily_balance[day] = 0
        
        # Calcula o saldo acumulado para cada dia
        accumulated = 0
        for transaction in transactions:
            day = int(transaction['date'].split('-')[2])
            amount = transaction['amount']
            if transaction['category_type'] == 'expense':
                amount = -amount
            
            accumulated += amount
            daily_balance[day] = accumulated
        
        # Prepara os dados para o gráfico
        days = list(daily_balance.keys())
        balances = list(daily_balance.values())
        
        # Cria o gráfico
        plt.figure(figsize=(10, 4))
        plt.plot(days, balances, color=line_color, marker='o', linewidth=2)
        
        # Preenche a área sob a curva
        plt.fill_between(days, balances, color=fill_color, alpha=0.3)
        
        # Adiciona rótulos e título
        plt.xlabel('Dias', color=text_color)
        plt.ylabel('Saldo (R$)', color=text_color)
        plt.title(f'Desempenho em {calendar.month_name[month]} de {year}', color=text_color)
        
        # Adiciona grid
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Adiciona alguns valores no gráfico
        for i, (day, balance) in enumerate(zip(days, balances)):
            if i == 0 or i == len(days) - 1 or abs(balance) > max(abs(b) for b in balances) * 0.5:
                plt.annotate(f'{balance:.2f}', (day, balance), 
                             textcoords="offset points", 
                             xytext=(0, 10), 
                             ha='center',
                             color=text_color)
        
        # Salva o gráfico em um buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Converte para QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())
        
        plt.close()
        
        return pixmap
    
    def generate_category_charts(self, year, month, theme="light"):
        """Gera gráficos de pizza para categorias de receita e despesa"""
        if not self.user_id:
            return None, None
        
        # Configura cores baseadas no tema
        if theme == "dark":
            plt.style.use('dark_background')
            text_color = 'white'
            colors_income = ['#9370DB', '#8A2BE2', '#9932CC', '#BA55D3', '#DA70D6']
            colors_expense = ['#9370DB', '#8A2BE2', '#9932CC', '#BA55D3', '#DA70D6', '#FF69B4', '#FF1493', '#C71585']
        else:
            plt.style.use('default')
            text_color = 'black'
            colors_income = ['#9370DB', '#8A2BE2', '#9932CC', '#BA55D3', '#DA70D6']
            colors_expense = ['#9370DB', '#8A2BE2', '#9932CC', '#BA55D3', '#DA70D6', '#FF69B4', '#FF1493', '#C71585']
        
        # Obtém o resumo mensal
        summary = self.get_monthly_summary(year, month)
        
        if not summary:
            return None, None
        
        # Gráfico de receitas
        income_pixmap = None
        if summary['income']['categories']:
            plt.figure(figsize=(6, 6))
            
            labels = [item['name'] for item in summary['income']['categories']]
            values = [item['total'] for item in summary['income']['categories']]
            
            plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors_income)
            plt.axis('equal')
            plt.title('Categorias de Receita', color=text_color)
            
            # Salva o gráfico em um buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            
            # Converte para QPixmap
            income_pixmap = QPixmap()
            income_pixmap.loadFromData(buf.getvalue())
            
            plt.close()
        
        # Gráfico de despesas
        expense_pixmap = None
        if summary['expense']['categories']:
            plt.figure(figsize=(6, 6))
            
            labels = [item['name'] for item in summary['expense']['categories']]
            values = [item['total'] for item in summary['expense']['categories']]
            
            plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors_expense)
            plt.axis('equal')
            plt.title('Categorias de Despesas', color=text_color)
            
            # Salva o gráfico em um buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            
            # Converte para QPixmap
            expense_pixmap = QPixmap()
            expense_pixmap.loadFromData(buf.getvalue())
            
            plt.close()
        
        return income_pixmap, expense_pixmap
    
    def generate_movement_chart(self, year, month, theme="light"):
        """Gera um gráfico de movimentação (receitas e despesas)"""
        if not self.user_id:
            return None
        
        # Configura cores baseadas no tema
        if theme == "dark":
            plt.style.use('dark_background')
            income_color = '#9370DB'  # Roxo
            expense_color = '#FF1493'  # Rosa
            text_color = 'white'
        else:
            plt.style.use('default')
            income_color = '#9370DB'  # Roxo
            expense_color = '#FF1493'  # Rosa
            text_color = 'black'
        
        # Obtém o número de dias no mês
        _, num_days = calendar.monthrange(year, month)
        
        # Prepara as datas para o mês
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{num_days:02d}"
        
        # Obtém as transações do mês
        transactions = self.get_transactions(start_date, end_date)
        
        # Organiza as transações por dia
        daily_income = {}
        daily_expense = {}
        for day in range(1, num_days + 1):
            daily_income[day] = 0
            daily_expense[day] = 0
        
        # Calcula receitas e despesas para cada dia
        for transaction in transactions:
            day = int(transaction['date'].split('-')[2])
            amount = transaction['amount']
            
            if transaction['category_type'] == 'income':
                daily_income[day] += amount
            else:  # expense
                daily_expense[day] += amount
        
        # Prepara os dados para o gráfico
        days = list(range(1, num_days + 1))
        income_values = [daily_income[day] for day in days]
        expense_values = [daily_expense[day] for day in days]
        
        # Cria o gráfico
        plt.figure(figsize=(10, 4))
        
        # Plota receitas e despesas
        plt.plot(days, income_values, color=income_color, marker='o', linewidth=2, label='Receitas')
        plt.plot(days, expense_values, color=expense_color, marker='o', linewidth=2, label='Despesas')
        
        # Adiciona rótulos e título
        plt.xlabel('Dias', color=text_color)
        plt.ylabel('Valor (R$)', color=text_color)
        plt.title(f'Movimentação em {calendar.month_name[month]} de {year}', color=text_color)
        
        # Adiciona legenda
        plt.legend()
        
        # Adiciona grid
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Adiciona alguns valores no gráfico
        for i, (day, income, expense) in enumerate(zip(days, income_values, expense_values)):
            if income > 0 and (i == 0 or i == len(days) - 1 or income > max(income_values) * 0.5):
                plt.annotate(f'{income:.2f}', (day, income), 
                             textcoords="offset points", 
                             xytext=(0, 10), 
                             ha='center',
                             color=income_color)
            
            if expense > 0 and (i == 0 or i == len(days) - 1 or expense > max(expense_values) * 0.5):
                plt.annotate(f'{expense:.2f}', (day, expense), 
                             textcoords="offset points", 
                             xytext=(0, -15), 
                             ha='center',
                             color=expense_color)
        
        # Salva o gráfico em um buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Converte para QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())
        
        plt.close()
        
        return pixmap