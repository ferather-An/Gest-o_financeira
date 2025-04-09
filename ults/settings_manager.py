import json
import os
from pathlib import Path

class SettingsManager:
    def __init__(self):
        # Cria o diretório de configurações se não existir
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "settings.json"
        
        # Configurações padrão
        self.default_settings = {
            "theme": "light",
            "font_family": "Arial",
            "font_size": 10,
            "color_scheme": "default",
            "backup_dir": str(Path("data/backups")),
            "export_dir": str(Path("data/exports")),
            "auto_backup": True,
            "backup_interval": 7  # dias
        }
        
        # Carrega as configurações
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Carrega as configurações do arquivo"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Garante que todas as configurações padrão estejam presentes
                for key, value in self.default_settings.items():
                    if key not in settings:
                        settings[key] = value
                
                return settings
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")
                return self.default_settings.copy()
        else:
            # Cria o arquivo de configurações com os valores padrão
            self.save_settings(self.default_settings)
            return self.default_settings.copy()
    
    def save_settings(self, settings=None):
        """Salva as configurações no arquivo"""
        if settings is None:
            settings = self.settings
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False
    
    def get_setting(self, key, default=None):
        """Obtém uma configuração específica"""
        return self.settings.get(key, default)
    
    def set_setting(self, key, value):
        """Define uma configuração específica"""
        self.settings[key] = value
        return self.save_settings()
    
    def reset_to_default(self):
        """Redefine todas as configurações para os valores padrão"""
        self.settings = self.default_settings.copy()
        return self.save_settings()