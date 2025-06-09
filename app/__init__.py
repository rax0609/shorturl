from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.models.models import db
from app.config.config import config_by_name
import os

def create_app(config_name='default'):
    """創建 Flask 應用程式
    
    此函數是應用程式的工廠函數，負責初始化Flask應用，
    配置各種擴展，註冊路由藍圖，並設置資料庫。
    
    參數:
        config_name (str): 配置名稱，用於選擇不同環境的配置，預設為'default'
        
    返回:
        Flask: 配置完成的Flask應用程式實例
    """
    # 創建Flask應用程式實例
    app = Flask(__name__)
    
    # 從config_by_name字典中載入對應名稱的配置類別
    app.config.from_object(config_by_name[config_name])
    
    # 初始化CORS擴展，允許跨域請求，解決前端與後端分離架構的跨域問題
    CORS(app)
    
    # 初始化JWT管理器，用於處理使用者認證和授權
    jwt = JWTManager(app)
    
    # 將Flask應用程式實例綁定到SQLAlchemy，初始化ORM
    db.init_app(app)
    
    # 引入並註冊各個功能模塊的藍圖(Blueprint)
    # 這些引入放在函數內部避免循環引入問題
    from app.routes.auth_routes import auth_bp  # 身份認證相關路由
    from app.routes.url_routes import url_bp    # 短網址相關路由
    from app.routes.admin_routes import admin_bp  # 管理員相關路由
    
    # 註冊藍圖並設定URL前綴，組織API結構
    app.register_blueprint(auth_bp, url_prefix='/api/auth')  # 身份認證API
    app.register_blueprint(url_bp, url_prefix='/api/urls')   # 短網址API
    app.register_blueprint(admin_bp, url_prefix='/api/admin')  # 管理員API
    
    # 檢查資料庫是否存在，如果不存在則創建資料庫和表
    with app.app_context():  # 建立應用程式上下文，讓資料庫操作在正確的環境中執行
        # 從資料庫URI中提取SQLite資料庫文件路徑
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        # 檢查資料庫文件是否存在
        if not os.path.exists(db_path):
            # 若不存在，則創建所有資料表
            db.create_all()
            # 引入建立預設管理員帳號所需的函數和模型
            from app.utils.helpers import hash_password
            from app.models.models import User, UserRole
            
            # 檢查是否已存在管理員帳號
            admin = User.query.filter_by(role=UserRole.ADMIN).first()
            # 如果不存在管理員，則創建一個預設管理員帳號
            if not admin:
                # 創建管理員使用者實例
                admin = User(
                    username='admin',  # 預設使用者名稱
                    email='admin@example.com',  # 預設電子郵件
                    password_hash=hash_password('admin123'),  # 加密預設密碼
                    role=UserRole.ADMIN  # 設定為管理員角色
                )
                # 將管理員帳號添加到資料庫會話中
                db.session.add(admin)
                # 提交事務，將數據持久化到資料庫
                db.session.commit()
    
    # 返回配置完成的Flask應用程式實例
    return app
