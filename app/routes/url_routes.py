# filepath: c:\code\stust\shorturl\app\routes\url_routes.py
# 引入Flask相關模組，用於API路由和請求處理
from flask import Blueprint, request, jsonify, redirect, current_app
# 引入JWT相關函數，用於使用者身份驗證
from flask_jwt_extended import jwt_required, get_jwt_identity
# 引入自定義的數據模型類
from app.models.models import URL, URLVisit, User, db
# 引入自定義的工具函數
from app.utils.helpers import generate_short_code, get_client_info
# 引入日期時間相關模組，用於處理過期時間
from datetime import datetime, timedelta
# 引入SQLAlchemy的desc函數，用於查詢結果排序
from sqlalchemy import desc
# 引入json模組，用於處理JSON格式數據
import json

# 創建一個藍圖(Blueprint)，用於組織URL相關的路由
url_bp = Blueprint('url', __name__)

@url_bp.route('/', methods=['POST'])
@jwt_required()  # 要求用戶必須通過JWT身份驗證才能存取此端點
def create_url():
    """建立新短網址"""
    # 獲取當前已驗證用戶的ID
    user_id = get_jwt_identity()
    # 獲取通過JSON傳來的請求數據
    data = request.get_json()
    
    # 檢查必要欄位是否存在
    if 'original_url' not in data:
        # 若缺少原始網址，返回錯誤信息
        return jsonify({'message': '缺少原始網址'}), 400
    
    # 使用自定義函數生成短網址代碼
    short_code = generate_short_code()
    
    # 確保短碼在資料庫中是唯一的
    while URL.query.filter_by(short_code=short_code).first():
        # 如果已存在，重新生成一個新的短碼
        short_code = generate_short_code()
    
    # 處理過期時間設定
    expires_at = None
    if 'expires_days' in data and data['expires_days']:
        # 若指定了過期天數，計算過期時間
        expires_at = datetime.utcnow() + timedelta(days=int(data['expires_days']))
    
    # 建立新的URL對象
    new_url = URL(
        original_url=data['original_url'],  # 設置原始網址
        short_code=short_code,  # 設置短碼
        title=data.get('title', ''),  # 設置標題，若未提供則為空字串
        user_id=user_id,  # 關聯到當前用戶
        expires_at=expires_at  # 設置過期時間
    )
    
    # 將新URL對象添加到資料庫會話中
    db.session.add(new_url)
    # 提交事務，將數據持久化到資料庫
    db.session.commit()
    
    # 構建完整的短網址，包含域名和短碼
    short_url = f"{current_app.config['DOMAIN']}/s/{short_code}"
    
    # 返回成功信息和新建的短網址數據
    return jsonify({
        'message': '短網址建立成功',
        'url': {
            'id': new_url.id,
            'original_url': new_url.original_url,
            'short_code': new_url.short_code,
            'short_url': short_url,
            'title': new_url.title,
            'created_at': new_url.created_at.isoformat(),  # 轉換為ISO格式字串
            'expires_at': new_url.expires_at.isoformat() if new_url.expires_at else None,
            'is_active': new_url.is_active
        }
    }), 201  # HTTP 201狀態碼表示資源創建成功

@url_bp.route('/', methods=['GET'])
@jwt_required()  # 要求用戶必須通過JWT身份驗證才能存取此端點
def get_user_urls():
    """獲取當前使用者的短網址列表"""
    # 獲取當前已驗證用戶的ID
    user_id = get_jwt_identity()
    
    # 獲取分頁參數，默認為第1頁，每頁10條記錄
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 獲取篩選條件參數
    is_active = request.args.get('is_active')  # 是否只顯示活躍的短網址
    search = request.args.get('search')  # 搜尋關鍵詞
    
    # 創建基本查詢，過濾出屬於當前用戶的短網址
    query = URL.query.filter_by(user_id=user_id)
    
    # 根據活躍狀態進行篩選
    if is_active is not None:
        # 將字串轉換為布林值
        is_active = is_active.lower() == 'true'
        # 應用篩選條件
        query = query.filter_by(is_active=is_active)
    
    # 根據搜尋關鍵詞進行篩選
    if search:
        # 使用OR條件搜尋原始網址、短碼或標題中包含關鍵詞的記錄
        query = query.filter(
            (URL.original_url.like(f'%{search}%')) |
            (URL.short_code.like(f'%{search}%')) |
            (URL.title.like(f'%{search}%'))
        )
    
    # 按創建時間降序排序
    query = query.order_by(desc(URL.created_at))
    
    # 應用分頁
    urls_pagination = query.paginate(page=page, per_page=per_page)
    
    # 初始化空列表，用於存放格式化後的URL數據
    urls = []
    # 遍歷分頁後的URL記錄
    for url in urls_pagination.items:
        # 構建完整的短網址
        short_url = f"{current_app.config['DOMAIN']}/s/{url.short_code}"
        # 將URL數據格式化為字典並添加到列表中
        urls.append({
            'id': url.id,
            'original_url': url.original_url,
            'short_code': url.short_code,
            'short_url': short_url,
            'title': url.title,
            'created_at': url.created_at.isoformat(),
            'expires_at': url.expires_at.isoformat() if url.expires_at else None,
            'is_active': url.is_active,
            'visit_count': url.visit_count  # 訪問次數
        })
    
    # 返回URL列表和分頁信息
    return jsonify({
        'urls': urls,  # URL數據列表
        'total': urls_pagination.total,  # 總記錄數
        'pages': urls_pagination.pages,  # 總頁數
        'page': page,  # 當前頁碼
        'per_page': per_page  # 每頁記錄數
    }), 200  # HTTP 200狀態碼表示請求成功

@url_bp.route('/<int:url_id>', methods=['GET'])
@jwt_required()  # 要求用戶必須通過JWT身份驗證才能存取此端點
def get_url(url_id):
    """獲取指定短網址的詳情"""
    # 獲取當前已驗證用戶的ID
    user_id = get_jwt_identity()
    
    # 根據ID查詢短網址記錄
    url = URL.query.get(url_id)
    
    # 檢查記錄是否存在
    if not url:
        # 若不存在，返回錯誤信息
        return jsonify({'message': '短網址不存在'}), 404
    
    # 檢查當前用戶是否有權限訪問此短網址
    user = User.query.get(user_id)
    # 只有短網址擁有者或管理員可以訪問
    if url.user_id != user_id and user.role.value != 'admin':
        # 若無權限，返回錯誤信息
        return jsonify({'message': '無權訪問'}), 403
    
    # 構建完整的短網址
    short_url = f"{current_app.config['DOMAIN']}/s/{url.short_code}"
    
    # 初始化空列表，用於存放訪問記錄數據
    visits = []
    # 遍歷短網址的所有訪問記錄
    for visit in url.visits:
        # 將訪問記錄格式化為字典並添加到列表中
        visits.append({
            'id': visit.id,
            'ip_address': visit.ip_address,  # 訪問者IP地址
            'user_agent': visit.user_agent,  # 訪問者瀏覽器信息
            'referer': visit.referer,  # 來源頁面
            'timestamp': visit.timestamp.isoformat()  # 訪問時間
        })
    
    # 返回短網址詳情和訪問記錄
    return jsonify({
        'url': {
            'id': url.id,
            'original_url': url.original_url,
            'short_code': url.short_code,
            'short_url': short_url,
            'title': url.title,
            'created_at': url.created_at.isoformat(),
            'updated_at': url.updated_at.isoformat(),
            'expires_at': url.expires_at.isoformat() if url.expires_at else None,
            'is_active': url.is_active,
            'visit_count': url.visit_count  # 訪問次數
        },
        'visits': visits  # 訪問記錄列表
    }), 200  # HTTP 200狀態碼表示請求成功

@url_bp.route('/<int:url_id>', methods=['PUT'])
@jwt_required()  # 要求用戶必須通過JWT身份驗證才能存取此端點
def update_url(url_id):
    """更新短網址資訊"""
    # 獲取當前已驗證用戶的ID
    user_id = get_jwt_identity()
    
    # 根據ID查詢短網址記錄
    url = URL.query.get(url_id)
    
    # 檢查記錄是否存在
    if not url:
        # 若不存在，返回錯誤信息
        return jsonify({'message': '短網址不存在'}), 404
    
    # 檢查當前用戶是否有權限更新此短網址
    user = User.query.get(user_id)
    # 只有短網址擁有者或管理員可以更新
    if url.user_id != user_id and user.role.value != 'admin':
        # 若無權限，返回錯誤信息
        return jsonify({'message': '無權更新'}), 403
    
    # 獲取通過JSON傳來的更新數據
    data = request.get_json()
    # 標記是否有數據更新
    updated = False
    
    # 更新標題（如果提供了新標題）
    if 'title' in data:
        url.title = data['title']
        updated = True
    
    # 更新原始網址（如果提供了新的原始網址）
    if 'original_url' in data:
        url.original_url = data['original_url']
        updated = True
    
    # 更新活躍狀態（如果提供了新的活躍狀態）
    if 'is_active' in data:
        url.is_active = data['is_active']
        updated = True
    
    # 更新過期時間（如果提供了新的過期天數）
    if 'expires_days' in data:
        if data['expires_days']:
            # 計算新的過期時間
            url.expires_at = datetime.utcnow() + timedelta(days=int(data['expires_days']))
        else:
            # 若過期天數為空，則設為永不過期
            url.expires_at = None
        updated = True
    
    # 如果有數據更新，則保存到資料庫
    if updated:
        # 提交事務，將更新持久化到資料庫
        db.session.commit()
        
        # 構建完整的短網址
        short_url = f"{current_app.config['DOMAIN']}/s/{url.short_code}"
        
        # 返回成功信息和更新後的短網址數據
        return jsonify({
            'message': '短網址更新成功',
            'url': {
                'id': url.id,
                'original_url': url.original_url,
                'short_code': url.short_code,
                'short_url': short_url,
                'title': url.title,
                'created_at': url.created_at.isoformat(),
                'updated_at': url.updated_at.isoformat(),
                'expires_at': url.expires_at.isoformat() if url.expires_at else None,
                'is_active': url.is_active
            }
        }), 200  # HTTP 200狀態碼表示請求成功
    else:
        # 若沒有數據更新，也返回成功信息
        return jsonify({'message': '無資料更新'}), 200

@url_bp.route('/<int:url_id>', methods=['DELETE'])
@jwt_required()  # 要求用戶必須通過JWT身份驗證才能存取此端點
def delete_url(url_id):
    """刪除短網址"""
    # 獲取當前已驗證用戶的ID
    user_id = get_jwt_identity()
    
    # 根據ID查詢短網址記錄
    url = URL.query.get(url_id)
    
    # 檢查記錄是否存在
    if not url:
        # 若不存在，返回錯誤信息
        return jsonify({'message': '短網址不存在'}), 404
    
    # 檢查當前用戶是否有權限刪除此短網址
    user = User.query.get(user_id)
    # 只有短網址擁有者或管理員可以刪除
    if url.user_id != user_id and user.role.value != 'admin':
        # 若無權限，返回錯誤信息
        return jsonify({'message': '無權刪除'}), 403
    
    # 從資料庫中刪除短網址記錄
    db.session.delete(url)
    # 提交事務，將刪除操作持久化到資料庫
    db.session.commit()
    
    # 返回成功信息
    return jsonify({'message': '短網址刪除成功'}), 200

@url_bp.route('/s/<short_code>', methods=['GET'])
def redirect_to_url(short_code):
    """短網址跳轉"""
    # 根據短碼查詢短網址記錄
    url = URL.query.filter_by(short_code=short_code).first()
    
    # 檢查記錄是否存在
    if not url:
        # 若不存在，返回錯誤信息
        return jsonify({'message': '短網址不存在'}), 404
    
    # 檢查短網址是否啟用
    if not url.is_active:
        # 若已停用，返回錯誤信息
        return jsonify({'message': '此短網址已被停用'}), 403
    
    # 檢查短網址是否過期
    if url.expires_at and url.expires_at < datetime.utcnow():
        # 若已過期，返回錯誤信息
        return jsonify({'message': '此短網址已過期'}), 403
    
    # 獲取訪問者的客戶端信息
    client_info = get_client_info()
    
    # 創建新的訪問記錄
    url_visit = URLVisit(
        url_id=url.id,  # 關聯到當前短網址
        ip_address=client_info['ip_address'],  # 訪問者IP地址
        user_agent=client_info['user_agent'],  # 訪問者瀏覽器信息
        referer=client_info['referer']  # 來源頁面
    )
    
    # 將訪問記錄添加到資料庫會話中
    db.session.add(url_visit)
    # 提交事務，將數據持久化到資料庫
    db.session.commit()
    
    # 跳轉到原始網址
    return redirect(url.original_url)
