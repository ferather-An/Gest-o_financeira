import datetime
import calendar
import locale
import os
import platform

def format_currency(value):
    """Formata um valor como moeda (R$)"""
    return f"R$ {value:.2f}"

def format_date(date_str, output_format="%d/%m/%Y"):
    """Formata uma data no formato desejado"""
    if isinstance(date_str, str):
        # Assume que a data está no formato ISO (YYYY-MM-DD)
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    else:
        # Assume que é um objeto datetime
        date_obj = date_str
    
    return date_obj.strftime(output_format)

def get_month_name(month_number):
    """Retorna o nome do mês em português"""
    # Configura o locale para português do Brasil
    try:
        if platform.system() == 'Windows':
            locale.setlocale(locale.LC_TIME, 'pt_BR')
        else:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        # Se não conseguir configurar o locale, usa os nomes em inglês
        month_names = [
            "Janeiro", "Fevereiro", "Março", "Abril",
            "Maio", "Junho", "Julho", "Agosto",
            "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        return month_names[month_number - 1]
    
    # Retorna o nome do mês
    return calendar.month_name[month_number].capitalize()

def get_month_days(year, month):
    """Retorna o número de dias em um mês"""
    return calendar.monthrange(year, month)[1]

def get_first_day_of_month(year, month):
    """Retorna o primeiro dia do mês no formato ISO"""
    return f"{year}-{month:02d}-01"

def get_last_day_of_month(year, month):
    """Retorna o último dia do mês no formato ISO"""
    last_day = get_month_days(year, month)
    return f"{year}-{month:02d}-{last_day:02d}"

def get_first_day_of_year(year):
    """Retorna o primeiro dia do ano no formato ISO"""
    return f"{year}-01-01"

def get_last_day_of_year(year):
    """Retorna o último dia do ano no formato ISO"""
    return f"{year}-12-31"

def create_directory_if_not_exists(directory_path):
    """Cria um diretório se ele não existir"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return directory_path

def is_valid_email(email):
    """Verifica se um e-mail é válido"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def calculate_percentage(value, total):
    """Calcula a porcentagem de um valor em relação ao total"""
    if total == 0:
        return 0
    return (value / total) * 100