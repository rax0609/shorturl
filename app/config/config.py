import os
from datetime import timedelta
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

class Config:
    """基礎配置類"""
    # Flask 設定
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev_key')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # 資料庫設定
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///shorturl.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT 設定
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))
    )
    
    # 短網址設定
    DOMAIN = os.getenv('DOMAIN', 'http://localhost:5000')

class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False

# 配置字典
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
