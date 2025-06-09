# 引入 SQLAlchemy 套件，用於處理資料庫操作和ORM映射
from flask_sqlalchemy import SQLAlchemy
# 引入 datetime 模組，用於處理日期和時間
from datetime import datetime
# 引入 enum 模組，用於定義列舉類型
import enum

# 初始化 SQLAlchemy 物件，此物件將用於定義資料庫模型和進行資料庫操作
db = SQLAlchemy()

class UserRole(enum.Enum):
    """使用者角色"""
    # 定義一般使用者角色
    USER = 'user'
    # 定義管理員角色
    ADMIN = 'admin'

class User(db.Model):
    """使用者模型 - 用於儲存使用者資訊"""
    # 指定資料表名稱
    __tablename__ = 'users'
    
    # 定義使用者ID欄位，設為主鍵
    id = db.Column(db.Integer, primary_key=True)
    # 定義使用者名稱欄位，必須唯一且不為空
    username = db.Column(db.String(50), unique=True, nullable=False)
    # 定義電子郵件欄位，必須唯一且不為空
    email = db.Column(db.String(100), unique=True, nullable=False)
    # 定義密碼雜湊欄位，存儲加密後的密碼
    password_hash = db.Column(db.String(100), nullable=False)
    # 定義角色欄位，使用UserRole枚舉類型，預設為一般使用者
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    # 定義活躍狀態欄位，預設為活躍(True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    # 定義建立時間欄位，預設為目前UTC時間
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # 定義更新時間欄位，在初始建立與每次更新時自動設置為目前UTC時間
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 定義與URL模型的一對多關聯，當使用者被刪除時，其所有短網址也會被刪除
    # lazy=True 表示關聯資料會在需要時才被載入，提高效能
    # cascade="all, delete-orphan" 表示當使用者被刪除時，級聯刪除相關的URL記錄
    urls = db.relationship('URL', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        """定義物件的字串表示形式，方便除錯和日誌記錄"""
        return f'<User {self.username}>'

class URL(db.Model):
    """短網址模型 - 用於儲存短網址和原始網址的映射關係"""
    # 指定資料表名稱
    __tablename__ = 'urls'
    
    # 定義短網址ID欄位，設為主鍵
    id = db.Column(db.Integer, primary_key=True)
    # 定義原始網址欄位，用於存儲要縮短的完整URL
    original_url = db.Column(db.String(2000), nullable=False)
    # 定義短碼欄位，必須唯一且不為空，並加上索引以提高查詢效能
    short_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    # 定義標題欄位，用於描述此短網址的用途，可為空
    title = db.Column(db.String(200), nullable=True)
    # 定義活躍狀態欄位，預設為活躍(True)，表示此短網址是否可用
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    # 定義建立時間欄位，預設為目前UTC時間
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # 定義更新時間欄位，在初始建立與每次更新時自動設置為目前UTC時間
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # 定義過期時間欄位，若設置則表示短網址的有效期限，可為空
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # 定義外鍵，關聯到使用者表的ID欄位
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 定義與URLVisit模型的一對多關聯，當短網址被刪除時，其所有訪問記錄也會被刪除
    visits = db.relationship('URLVisit', backref='url', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        """定義物件的字串表示形式，顯示短碼和部分原始URL"""
        return f'<URL {self.short_code}: {self.original_url[:30]}...>'
    
    @property
    def visit_count(self):
        """計算並返回短網址的訪問次數，使用屬性裝飾器讓它可作為屬性訪問"""
        return len(self.visits)

class URLVisit(db.Model):
    """短網址訪問記錄模型 - 用於追蹤短網址的訪問資訊"""
    # 指定資料表名稱
    __tablename__ = 'url_visits'
    
    # 定義訪問ID欄位，設為主鍵
    id = db.Column(db.Integer, primary_key=True)
    # 定義訪問者IP地址欄位，可為空，長度支持IPv6格式
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 最長 45 字元
    # 定義訪問者瀏覽器和設備資訊欄位
    user_agent = db.Column(db.String(255), nullable=True)
    # 定義來源頁面(referer)欄位，記錄訪問者來自哪個頁面
    referer = db.Column(db.String(500), nullable=True)
    # 定義訪問時間欄位，預設為目前UTC時間
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 定義外鍵，關聯到URL表的ID欄位
    url_id = db.Column(db.Integer, db.ForeignKey('urls.id'), nullable=False)
    
    def __repr__(self):
        """定義物件的字串表示形式，顯示訪問的URL ID和時間戳記"""
        return f'<URLVisit {self.url_id} at {self.timestamp}>'
