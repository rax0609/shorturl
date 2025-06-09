# 引入Flask相關模組，用於處理HTTP請求和回應
from flask import Blueprint, request, jsonify
# 引入JWT相關函數，用於處理JSON Web Token的建立和驗證
from flask_jwt_extended import (
    create_access_token, get_jwt_identity, jwt_required
)
# 引入自定義的數據模型類和資料庫物件
from app.models.models import User, db
# 引入密碼雜湊和校驗的工具函數
from app.utils.helpers import hash_password, check_password

# 創建一個藍圖(Blueprint)，用於組織身份驗證相關的路由
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """使用者註冊"""
    # 獲取通過JSON傳來的註冊數據
    data = request.get_json()
    
    # 檢查是否包含所有必要的註冊欄位
    if not all(key in data for key in ['username', 'email', 'password']):
        # 若缺少必要欄位，返回錯誤信息
        return jsonify({'message': '缺少必要欄位'}), 400
    
    # 檢查使用者名稱是否已存在
    if User.query.filter_by(username=data['username']).first():
        # 若使用者名稱已存在，返回衝突錯誤信息
        return jsonify({'message': '使用者名稱已存在'}), 409
    
    # 檢查電子郵件是否已存在
    if User.query.filter_by(email=data['email']).first():
        # 若電子郵件已存在，返回衝突錯誤信息
        return jsonify({'message': '電子郵件已存在'}), 409
    
    # 創建新的使用者對象，並設置其屬性
    user = User(
        username=data['username'],  # 設置使用者名稱
        email=data['email'],  # 設置電子郵件
        password_hash=hash_password(data['password'])  # 將密碼進行雜湊處理後存儲
    )
    
    # 將新使用者對象添加到資料庫會話中
    db.session.add(user)
    # 提交事務，將數據持久化到資料庫
    db.session.commit()
    
    # 創建JWT訪問令牌，用於後續的用戶身份驗證
    access_token = create_access_token(
        identity=str(user.id),  # 使用用戶ID作為身份標識
        additional_claims={  # 添加額外的聲明資訊
            'username': user.username,
            'role': user.role.value
        }
    )
    
    # 返回註冊成功信息、訪問令牌和用戶資料
    return jsonify({
        'message': '註冊成功',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value
        }
    }), 201  # HTTP 201狀態碼表示資源創建成功

@auth_bp.route('/login', methods=['POST'])
def login():
    """使用者登入"""
    # 獲取通過JSON傳來的登入數據
    data = request.get_json()
    
    # 檢查是否包含所有必要的登入欄位
    if not all(key in data for key in ['username', 'password']):
        # 若缺少必要欄位，返回錯誤信息
        return jsonify({'message': '缺少使用者名稱或密碼'}), 400
    
    # 根據使用者名稱查詢使用者
    user = User.query.filter_by(username=data['username']).first()
    
    # 驗證使用者存在且密碼正確
    if not user or not check_password(data['password'], user.password_hash):
        # 若驗證失敗，返回未授權錯誤信息
        return jsonify({'message': '使用者名稱或密碼錯誤'}), 401
    
    # 檢查使用者帳戶是否已被停用
    if not user.is_active:
        # 若帳戶已停用，返回禁止訪問錯誤信息
        return jsonify({'message': '帳號已被停用'}), 403
    
    # 創建JWT訪問令牌，用於後續的用戶身份驗證
    access_token = create_access_token(
        identity=str(user.id),  # 使用用戶ID作為身份標識
        additional_claims={  # 添加額外的聲明資訊
            'username': user.username,
            'role': user.role.value
        }
    )
    
    # 返回登入成功信息、訪問令牌和用戶資料
    return jsonify({
        'message': '登入成功',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value
        }
    }), 200  # HTTP 200狀態碼表示請求成功

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()  # 要求用戶必須通過JWT身份驗證才能存取此端點
def profile():
    """獲取當前使用者資料"""
    # 獲取當前已驗證用戶的ID
    user_id = get_jwt_identity()
    # 根據ID查詢用戶
    user = User.query.get(user_id)
    
    # 檢查用戶是否存在
    if not user:
        # 若不存在，返回不存在錯誤信息
        return jsonify({'message': '使用者不存在'}), 404
    
    # 檢查用戶帳戶是否已被停用
    if not user.is_active:
        # 若帳戶已停用，返回禁止訪問錯誤信息
        return jsonify({'message': '帳號已被停用'}), 403
    
    # 返回用戶資料
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'created_at': user.created_at.isoformat(),  # 轉換為ISO格式字串
            'updated_at': user.updated_at.isoformat()  # 轉換為ISO格式字串
        }
    }), 200  # HTTP 200狀態碼表示請求成功

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()  # 要求用戶必須通過JWT身份驗證才能存取此端點
def update_profile():
    """更新使用者資料"""
    # 獲取當前已驗證用戶的ID
    user_id = get_jwt_identity()
    # 根據ID查詢用戶
    user = User.query.get(user_id)
    
    # 檢查用戶是否存在
    if not user:
        # 若不存在，返回不存在錯誤信息
        return jsonify({'message': '使用者不存在'}), 404
    
    # 檢查用戶帳戶是否已被停用
    if not user.is_active:
        # 若帳戶已停用，返回禁止訪問錯誤信息
        return jsonify({'message': '帳號已被停用'}), 403
    
    # 獲取通過JSON傳來的更新數據
    data = request.get_json()
    # 標記是否有數據更新
    updated = False
    
    # 更新電子郵件（如果提供了新的電子郵件且與當前不同）
    if 'email' in data and data['email'] != user.email:
        # 檢查新的電子郵件是否已被其他使用者使用
        if User.query.filter_by(email=data['email']).first():
            # 若電子郵件已被使用，返回衝突錯誤信息
            return jsonify({'message': '電子郵件已被使用'}), 409
        # 更新用戶的電子郵件
        user.email = data['email']
        updated = True
    
    # 更新密碼（如果提供了當前密碼和新密碼）
    if 'current_password' in data and 'new_password' in data:
        # 驗證當前密碼是否正確
        if not check_password(data['current_password'], user.password_hash):
            # 若當前密碼錯誤，返回未授權錯誤信息
            return jsonify({'message': '目前密碼錯誤'}), 401
        # 更新用戶的密碼雜湊
        user.password_hash = hash_password(data['new_password'])
        updated = True
    
    # 如果有數據更新，則保存到資料庫
    if updated:
        # 提交事務，將更新持久化到資料庫
        db.session.commit()
        # 返回更新成功信息
        return jsonify({'message': '資料更新成功'}), 200
    else:
        # 若沒有數據更新，也返回成功信息
        return jsonify({'message': '無資料更新'}), 200
