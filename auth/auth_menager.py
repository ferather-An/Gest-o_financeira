from database.db_manager import DatabaseManager

class AuthManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.current_user = None
    
    def login(self, username, password):
        """Realiza o login do usuário"""
        user = self.db_manager.authenticate_user(username, password)
        if user:
            self.current_user = user
            return True
        return False
    
    def logout(self):
        """Realiza o logout do usuário"""
        self.current_user = None
    
    def register(self, username, password, full_name, email=None):
        """Registra um novo usuário"""
        user_id = self.db_manager.register_user(username, password, full_name, email)
        return user_id is not None
    
    def get_current_user(self):
        """Retorna o usuário atual"""
        return self.current_user
    
    def is_authenticated(self):
        """Verifica se há um usuário autenticado"""
        return self.current_user is not None
    
    def update_settings(self, settings):
        """Atualiza as configurações do usuário atual"""
        if self.current_user:
            self.db_manager.update_user_settings(self.current_user["id"], settings)
            # Atualiza o objeto do usuário atual
            self.current_user["settings"] = settings
            return True
        return False