from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text
import json
import hashlib
import uuid

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求(方便前后端分离开发)

# 数据库配置(SQLite,无需额外安装数据库)
import os
db_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance', 'campus_secondhand.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 创建数据库对象
db = SQLAlchemy(app)


def parse_image_values(value):
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        text_value = value.strip()
        if not text_value:
            return []
        if text_value.startswith('['):
            try:
                parsed = json.loads(text_value)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except Exception:
                pass
        if '|||' in text_value:
            return [item.strip() for item in text_value.split('|||') if item.strip()]
        if ',' in text_value:
            return [item.strip() for item in text_value.split(',') if item.strip()]
        return [text_value]
    return [str(value).strip()] if str(value).strip() else []


def serialize_image_values(value):
    return json.dumps(parse_image_values(value), ensure_ascii=False)


def to_public_image_url(value):
    if not value:
        return None
    image = str(value).strip()
    if not image:
        return None
    if image.startswith(('http://', 'https://', 'data:')):
        return image
    if image.startswith('/'):
        return image
    return '/' + image


def first_image_url(value):
    images = parse_image_values(value)
    return to_public_image_url(images[0]) if images else None


DEFAULT_CATEGORY_TREE = [
    {'name': '数码产品', 'sort_order': 1, 'children': ['手机', '电脑', '耳机']},
    {'name': '书籍教材', 'sort_order': 2, 'children': ['教材教辅', '小说文学']},
    {'name': '生活用品', 'sort_order': 3, 'children': ['宿舍用品', '小电器']},
    {'name': '服饰鞋包', 'sort_order': 4, 'children': []},
    {'name': '运动户外', 'sort_order': 5, 'children': []},
    {'name': '其他', 'sort_order': 99, 'children': []},
]


def seed_default_categories():
    if Category.query.count() > 0:
        return

    category_records = []
    for parent_index, parent in enumerate(DEFAULT_CATEGORY_TREE, start=1):
        parent_category = Category(
            name=parent['name'],
            parent_id=0,
            sort_order=parent['sort_order'],
            status=1
        )
        db.session.add(parent_category)
        db.session.flush()
        category_records.append(parent_category)

        for child_index, child_name in enumerate(parent['children'], start=1):
            db.session.add(Category(
                name=child_name,
                parent_id=parent_category.id,
                sort_order=child_index,
                status=1
            ))

    db.session.commit()

# =====================================================
# 定义数据模型(映射到数据库表)
# =====================================================

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(50))
    student_id = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(500))
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    original_price = db.Column(db.Numeric(10, 2))
    images = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    condition = db.Column(db.String(20), default='good')
    status = db.Column(db.String(20), default='on_sale')
    views = db.Column(db.Integer, default=0)
    sales = db.Column(db.Integer, default=0)
    rating = db.Column(db.Numeric(2, 1), default=5.0)
    rating_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    parent_id = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(32), nullable=False, unique=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    merchant_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')
    receiver_name = db.Column(db.String(50))
    receiver_phone = db.Column(db.String(20))
    receiver_address = db.Column(db.String(500))
    payment_method = db.Column(db.String(20))
    remark = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Favorite(db.Model):
    __tablename__ = 'favorite'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    receiver_name = db.Column(db.String(50), nullable=False)
    receiver_phone = db.Column(db.String(20), nullable=False)
    campus_area = db.Column(db.String(100))
    detail_address = db.Column(db.String(255), nullable=False)
    is_default = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class SystemLog(db.Model):
    __tablename__ = 'system_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    action = db.Column(db.String(100), nullable=False)
    target = db.Column(db.String(200))
    ip_address = db.Column(db.String(45))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# =====================================================
# API 接口
# =====================================================

@app.route('/')
def index():
    """首页 - 直接返回前端页面"""
    return render_template('index.html')

@app.route('/test-db')
def test_db():
    """测试数据库连接"""
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({'status': 'success', 'message': '数据库连接成功!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/products', methods=['GET'])
def get_products():
    """获取商品列表"""
    try:
        products = Product.query.filter_by(status='on_sale').order_by(Product.created_at.desc()).limit(20).all()
        result = []
        for p in products:
            result.append({
                'id': p.id,
                'title': p.title,
                'price': float(p.price),
                'original_price': float(p.original_price) if p.original_price else None,
                'description': p.description or '',
                'condition': p.condition,
                'views': p.views,
                'stock': p.stock,
                'images': [to_public_image_url(img) for img in parse_image_values(p.images)]
            })
        return jsonify({'code': 200, 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/product/<int:id>', methods=['GET'])
def get_product(id):
    """获取商品详情"""
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({'code': 404, 'message': '商品不存在'})
        
        # 增加浏览量
        product.views += 1
        db.session.commit()
        
        return jsonify({'code': 200, 'data': {
            'id': product.id,
            'title': product.title,
            'price': float(product.price),
            'original_price': float(product.original_price) if product.original_price else None,
            'description': product.description,
            'condition': product.condition,
            'status': product.status,
            'views': product.views,
            'sales': product.sales,
            'stock': product.stock,
            'user_id': product.user_id,
            'category_id': product.category_id,
            'images': [to_public_image_url(img) for img in parse_image_values(product.images)]
        }})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/products/search', methods=['GET'])
def search_products():
    """搜索商品"""
    try:
        keyword = request.args.get('keyword', '')
        category_id = request.args.get('category_id', type=int)
        user_id = request.args.get('user_id', type=int)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        sort_by = request.args.get('sort_by', 'created_at')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Product.query.filter_by(status='on_sale')
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if keyword:
            category_ids = [cat.id for cat in Category.query.filter(Category.name.ilike(f'%{keyword}%')).all()]
            conditions = (Product.title.ilike(f'%{keyword}%')) | (Product.description.ilike(f'%{keyword}%'))
            if category_ids:
                conditions |= (Product.category_id.in_(category_ids))
            query = query.filter(conditions)
        
        if category_id:
            child_categories = Category.query.filter_by(parent_id=category_id).all()
            if child_categories:
                category_ids = [category_id] + [cat.id for cat in child_categories]
                query = query.filter(Product.category_id.in_(category_ids))
            else:
                query = query.filter_by(category_id=category_id)
        
        if min_price is not None and min_price > 0:
            query = query.filter(Product.price >= min_price)
        if max_price is not None and max_price > 0:
            query = query.filter(Product.price <= max_price)
        
        if sort_by == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(Product.price.desc())
        elif sort_by == 'sales_desc':
            query = query.order_by(Product.sales.desc())
        elif sort_by == 'views_desc':
            query = query.order_by(Product.views.desc())
        elif sort_by == 'rating_desc':
            query = query.order_by(Product.rating.desc())
        elif sort_by == 'created_at' or sort_by == 'all':
            query = query.order_by(Product.created_at.desc())
        else:
            query = query.order_by(Product.created_at.desc())
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for p in paginated.items:
            result.append({
                'id': p.id,
                'title': p.title,
                'price': float(p.price),
                'original_price': float(p.original_price) if p.original_price else None,
                'description': p.description[:100] if p.description else '',
                'views': p.views,
                'sales': p.sales,
                'stock': p.stock,
                'condition': p.condition or 'good',
                'rating': float(p.rating) if p.rating else 5.0,
                'rating_count': p.rating_count or 0,
                'images': [to_public_image_url(img) for img in parse_image_values(p.images)]
            })
        
        return jsonify({
            'code': 200,
            'data': result,
            'total': paginated.total,
            'page': page,
            'per_page': per_page,
            'total_pages': paginated.pages
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/product', methods=['POST'])
def create_product():
    """发布商品"""
    try:
        data = request.get_json()
        
        product = Product(
            user_id=data['user_id'],
            category_id=data.get('category_id'),
            title=data['title'],
            description=data.get('description'),
            price=data['price'],
            original_price=data.get('original_price'),
            images=serialize_image_values(data.get('images')) if data.get('images') else None,
            stock=data.get('stock', 0),
            condition=data.get('condition', 'good')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '商品发布成功', 'data': {'id': product.id}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/product/<int:id>', methods=['PUT'])
def update_product(id):
    """更新商品信息"""
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({'code': 404, 'message': '商品不存在'})
        
        data = request.get_json()
        
        if 'title' in data:
            product.title = data['title']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'original_price' in data:
            product.original_price = data['original_price']
        if 'category_id' in data:
            product.category_id = data['category_id']
        if 'condition' in data:
            product.condition = data['condition']
        if 'status' in data:
            product.status = data['status']
        if 'images' in data:
            product.images = serialize_image_values(data['images'])
        if 'stock' in data:
            product.stock = max(0, int(data['stock']))
        
        db.session.commit()
        return jsonify({'code': 200, 'message': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    """删除商品(硬删除)"""
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({'code': 404, 'message': '商品不存在'})
        
        # 硬删除商品
        db.session.delete(product)
        db.session.commit()
        return jsonify({'code': 200, 'message': '商品已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'code': 400, 'message': '用户名和密码不能为空'})
        
        existing = User.query.filter_by(username=data['username']).first()
        if existing:
            return jsonify({'code': 400, 'message': '用户名已存在'})
        
        hashed_pwd = hashlib.md5(data['password'].encode()).hexdigest()
        
        new_user = User(
            username=data['username'],
            password=hashed_pwd,
            real_name=data.get('real_name'),
            student_id=data.get('student_id'),
            phone=data.get('phone'),
            email=data.get('email')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '注册成功', 'data': {'id': new_user.id}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'code': 400, 'message': '用户名和密码不能为空'})
        
        hashed_pwd = hashlib.md5(data['password'].encode()).hexdigest()
        
        user = User.query.filter_by(
            username=data['username'],
            password=hashed_pwd
        ).first()
        
        if user:
            if user.status != 'active':
                return jsonify({'code': 403, 'message': '账号已被禁用'})
            return jsonify({'code': 200, 'message': '登录成功', 'data': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'real_name': user.real_name,
                'phone': user.phone,
                'email': user.email
            }})
        else:
            return jsonify({'code': 400, 'message': '用户名或密码错误'})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/user/<int:id>', methods=['GET'])
def get_user(id):
    """获取用户信息"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'})
        
        return jsonify({'code': 200, 'data': {
            'id': user.id,
            'username': user.username,
            'real_name': user.real_name,
            'student_id': user.student_id,
            'phone': user.phone,
            'email': user.email,
            'address': user.address,
            'role': user.role,
            'status': user.status
        }})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/user/<int:id>', methods=['PUT'])
def update_user(id):
    """更新用户信息"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'})
        
        data = request.get_json()
        
        if 'username' in data:
            # 检查用户名是否已被其他用户使用
            existing = User.query.filter(User.username == data['username'], User.id != id).first()
            if existing:
                return jsonify({'code': 400, 'message': '用户名已被使用'})
            user.username = data['username']
        if 'real_name' in data:
            user.real_name = data['real_name']
        if 'student_id' in data:
            user.student_id = data['student_id']
        if 'phone' in data:
            user.phone = data['phone']
        if 'email' in data:
            user.email = data['email']
        if 'address' in data:
            user.address = data['address']
        
        db.session.commit()
        return jsonify({'code': 200, 'message': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/user/change-password', methods=['POST'])
def change_password():
    """修改密码"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not user_id or not old_password or not new_password:
            return jsonify({'code': 400, 'message': '参数不能为空'})
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'})
        
        # 验证旧密码
        if user.password != hashlib.md5(old_password.encode()).hexdigest():
            return jsonify({'code': 400, 'message': '原密码错误'})
        
        # 更新新密码
        user.password = hashlib.md5(new_password.encode()).hexdigest()
        db.session.commit()
        return jsonify({'code': 200, 'message': '密码修改成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/user/bind-email', methods=['POST'])
def bind_email():
    """绑定邮箱"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        email = data.get('email')
        
        if not user_id or not email:
            return jsonify({'code': 400, 'message': '参数不能为空'})
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'})
        
        # 检查邮箱格式
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'code': 400, 'message': '邮箱格式不正确'})
        
        user.email = email
        db.session.commit()
        return jsonify({'code': 200, 'message': '邮箱绑定成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/user/bind-phone', methods=['POST'])
def bind_phone():
    """绑定手机"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        phone = data.get('phone')
        
        if not user_id or not phone:
            return jsonify({'code': 400, 'message': '参数不能为空'})
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'})
        
        # 检查手机号格式
        import re
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return jsonify({'code': 400, 'message': '手机号格式不正确'})
        
        user.phone = phone
        db.session.commit()
        return jsonify({'code': 200, 'message': '手机绑定成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/user/send-email-captcha', methods=['POST'])
def send_email_captcha():
    """发送邮箱验证码(模拟)"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'code': 400, 'message': '请输入邮箱地址'})
        
        # 模拟发送验证码
        print(f"模拟发送验证码到邮箱: {email}")
        return jsonify({'code': 200, 'message': '验证码已发送到邮箱'})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/user/send-phone-captcha', methods=['POST'])
def send_phone_captcha():
    """发送手机验证码(模拟)"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        
        if not phone:
            return jsonify({'code': 400, 'message': '请输入手机号码'})
        
        # 模拟发送验证码
        print(f"模拟发送验证码到手机: {phone}")
        return jsonify({'code': 200, 'message': '验证码已发送到手机'})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    """删除用户(注销账户)"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'})
        
        # 软删除或硬删除
        user.status = 'deleted'
        # 如果需要彻底删除,可以使用 db.session.delete(user)
        db.session.commit()
        return jsonify({'code': 200, 'message': '账户已注销'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取商品分类(支持多级嵌套)"""
    try:
        if Category.query.count() == 0:
            seed_default_categories()
        
        # 获取所有启用的分类
        all_categories = Category.query.filter_by(status=1).order_by(Category.sort_order).all()
        
        # 构建分类树
        category_map = {cat.id: cat for cat in all_categories}
        roots = []
        
        for category in all_categories:
            if category.parent_id == 0:
                # 顶级分类
                roots.append({
                    'id': category.id,
                    'name': category.name,
                    'children': build_category_children(category.id, category_map)
                })
        
        return jsonify({'code': 200, 'data': roots})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

def build_category_children(parent_id, category_map):
    """递归构建分类子节点"""
    children = []
    # 在实际应用中,可能需要按sort_order排序
    for category_id, category in category_map.items():
        if category.parent_id == parent_id:
            children.append({
                'id': category.id,
                'name': category.name,
                'children': build_category_children(category.id, category_map)
            })
    # 按sort_order排序
    children.sort(key=lambda x: next((cat.sort_order for cat in [category_map.get(x['id'])] if cat), 0))
    return children

@app.route('/api/products/suggest', methods=['GET'])
def search_suggestions():
    """搜索建议"""
    try:
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify({'code': 200, 'data': []})
        
        products = Product.query.filter(
            Product.status == 'on_sale',
            Product.title.ilike(f'%{keyword}%')
        ).limit(10).all()
        
        suggestions = list(set([p.title for p in products]))
        return jsonify({'code': 200, 'data': suggestions})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/products/hot-searches', methods=['GET'])
def hot_searches():
    """热门搜索"""
    try:
        hot_products = Product.query.filter_by(status='on_sale').order_by(Product.sales.desc()).limit(10).all()
        hot_titles = list(set([p.title.split()[0] if len(p.title.split()) > 0 else p.title for p in hot_products]))
        return jsonify({'code': 200, 'data': hot_titles[:8]})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})


@app.route('/api/admin/products', methods=['GET'])
def admin_get_products():
    """后台获取商品列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        keyword = request.args.get('keyword', '')
        status = request.args.get('status')
        category_id = request.args.get('category_id', type=int)

        query = db.session.query(Product, Category).outerjoin(Category, Product.category_id == Category.id)

        if keyword:
            query = query.filter(Product.title.ilike(f'%{keyword}%'))
        if status:
            query = query.filter(Product.status == status)
        if category_id:
            query = query.filter(Product.category_id == category_id)

        paginated = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        result = []
        for product, category in paginated.items:
            result.append({
                'id': product.id,
                'title': product.title,
                'category_id': product.category_id,
                'category_name': category.name if category else '',
                'price': float(product.price),
                'original_price': float(product.original_price) if product.original_price else None,
                'stock': product.stock,
                'condition': product.condition,
                'status': product.status,
                'views': product.views,
                'sales': product.sales,
                'images': [to_public_image_url(img) for img in parse_image_values(product.images)]
            })

        return jsonify({
            'code': 200,
            'data': result,
            'total': paginated.total,
            'page': page,
            'per_page': per_page,
            'total_pages': paginated.pages
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})


@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    """后台获取用户列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        keyword = request.args.get('keyword', '')
        status = request.args.get('status')
        role = request.args.get('role')

        query = User.query

        # 默认排除已删除的用户
        if status != 'deleted':
            query = query.filter(User.status != 'deleted')
        
        if keyword:
            query = query.filter(
                (User.username.ilike(f'%{keyword}%')) | 
                (User.real_name.ilike(f'%{keyword}%')) |
                (User.student_id.ilike(f'%{keyword}%'))
            )
        if status:
            query = query.filter(User.status == status)
        if role:
            query = query.filter(User.role == role)
        
        # 排除管理员用户(可选,这里保留显示所有用户)
        paginated = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        result = []
        for user in paginated.items:
            result.append({
                'id': user.id,
                'username': user.username,
                'real_name': user.real_name,
                'student_id': user.student_id,
                'phone': user.phone,
                'email': user.email,
                'role': user.role,
                'status': user.status,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None
            })

        return jsonify({
            'code': 200,
            'data': result,
            'total': paginated.total,
            'page': page,
            'per_page': per_page,
            'total_pages': paginated.pages
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})


@app.route('/api/admin/user/<int:id>/freeze', methods=['PUT'])
def admin_freeze_user(id):
    """冻结用户账户"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'})
        
        # 不能冻结管理员账户
        if user.role == 'admin':
            return jsonify({'code': 400, 'message': '不能冻结管理员账户'})
        
        user.status = 'frozen'
        db.session.commit()
        return jsonify({'code': 200, 'message': '用户账户已冻结'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})


@app.route('/api/admin/user/<int:id>/unfreeze', methods=['PUT'])
def admin_unfreeze_user(id):
    """解冻用户账户"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'})
        
        user.status = 'active'
        db.session.commit()
        return jsonify({'code': 200, 'message': '用户账户已解冻'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})


@app.route('/api/admin/user/<int:id>', methods=['DELETE'])
def admin_delete_user(id):
    """删除用户账户(硬删除)"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'})
        
        # 不能删除管理员账户
        if user.role == 'admin':
            return jsonify({'code': 400, 'message': '不能删除管理员账户'})
        
        # 删除该用户发布的所有商品
        Product.query.filter_by(user_id=id).delete()
        
        # 硬删除用户
        db.session.delete(user)
        db.session.commit()
        return jsonify({'code': 200, 'message': '用户账户已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})


@app.route('/api/admin/categories', methods=['GET'])
def admin_get_categories():
    """后台获取分类列表"""
    try:
        categories = Category.query.order_by(Category.parent_id.asc(), Category.sort_order.asc(), Category.id.asc()).all()
        result = []
        for category in categories:
            result.append({
                'id': category.id,
                'name': category.name,
                'parent_id': category.parent_id,
                'sort_order': category.sort_order,
                'status': category.status
            })
        return jsonify({'code': 200, 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})


@app.route('/api/category', methods=['POST'])
def create_category():
    """新增分类"""
    try:
        data = request.get_json()
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'code': 400, 'message': '分类名称不能为空'})

        category = Category(
            name=name,
            parent_id=int(data.get('parent_id', 0) or 0),
            sort_order=int(data.get('sort_order', 0) or 0),
            status=int(data.get('status', 1) or 1)
        )
        db.session.add(category)
        db.session.commit()
        return jsonify({'code': 200, 'message': '分类创建成功', 'data': {'id': category.id}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})


@app.route('/api/category/<int:id>', methods=['PUT'])
def update_category(id):
    """更新分类"""
    try:
        category = Category.query.get(id)
        if not category:
            return jsonify({'code': 404, 'message': '分类不存在'})

        data = request.get_json()
        if 'name' in data:
            name = (data.get('name') or '').strip()
            if not name:
                return jsonify({'code': 400, 'message': '分类名称不能为空'})
            category.name = name
        if 'parent_id' in data:
            category.parent_id = int(data.get('parent_id') or 0)
        if 'sort_order' in data:
            category.sort_order = int(data.get('sort_order') or 0)
        if 'status' in data:
            category.status = int(data.get('status') or 0)

        db.session.commit()
        return jsonify({'code': 200, 'message': '分类更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})


@app.route('/api/category/<int:id>', methods=['DELETE'])
def delete_category(id):
    """删除分类(硬删除)"""
    try:
        category = Category.query.get(id)
        if not category:
            return jsonify({'code': 404, 'message': '分类不存在'})

        # 硬删除分类
        db.session.delete(category)
        db.session.commit()
        return jsonify({'code': 200, 'message': '分类已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """获取购物车"""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'code': 400, 'message': 'user_id 参数缺失'})
        
        items = db.session.query(Cart, Product).join(
            Product, Cart.product_id == Product.id
        ).filter(Cart.user_id == user_id).all()
        
        result = []
        total = 0
        for cart, product in items:
            item_total = float(product.price) * cart.quantity
            total += item_total
            result.append({
                'id': cart.id,
                'product_id': product.id,
                'title': product.title,
                'price': float(product.price),
                'quantity': cart.quantity,
                'total': item_total,
                'image': first_image_url(product.images)
            })
        
        return jsonify({'code': 200, 'data': result, 'total_price': total})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    """添加商品到购物车"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not user_id or not product_id:
            return jsonify({'code': 400, 'message': 'user_id 和 product_id 不能为空'})
        
        product = Product.query.get(product_id)
        if not product or product.status != 'on_sale':
            return jsonify({'code': 400, 'message': '商品不存在或已下架'})
        if product.stock is not None and product.stock < quantity:
            return jsonify({'code': 400, 'message': '库存不足'})
        
        cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        
        db.session.commit()
        return jsonify({'code': 200, 'message': '添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/cart/<int:id>', methods=['PUT'])
def update_cart_item(id):
    """更新购物车商品数量"""
    try:
        cart_item = Cart.query.get(id)
        if not cart_item:
            return jsonify({'code': 404, 'message': '购物车项不存在'})
        
        data = request.get_json()
        if 'quantity' in data:
            new_quantity = int(data['quantity'])
            if new_quantity < 1:
                return jsonify({'code': 400, 'message': '数量不能小于1'})
            cart_item.quantity = new_quantity
        
        db.session.commit()
        return jsonify({'code': 200, 'message': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/cart/<int:id>', methods=['DELETE'])
def remove_from_cart(id):
    """从购物车移除商品"""
    try:
        cart_item = Cart.query.get(id)
        if not cart_item:
            return jsonify({'code': 404, 'message': '购物车项不存在'})
        
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'code': 200, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/order', methods=['POST'])
def create_order():
    """创建订单(支持直接购买和购物车购买两种方式)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'code': 400, 'message': 'user_id 不能为空'})
        
        # 方式一: 通过购物车ID创建订单
        cart_ids = data.get('cart_ids', [])
        
        # 方式二: 直接购买(立即购买)
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        orders = []
        
        if cart_ids and len(cart_ids) > 0:
            # 通过购物车创建订单
            cart_items = Cart.query.filter(Cart.id.in_(cart_ids), Cart.user_id == user_id).all()
            if not cart_items:
                return jsonify({'code': 400, 'message': '购物车为空'})
            
            for cart in cart_items:
                product = Product.query.get(cart.product_id)
                if not product or product.status != 'on_sale':
                    return jsonify({'code': 400, 'message': f'商品已下架'})
                if product.stock is not None and product.stock < cart.quantity:
                    return jsonify({'code': 400, 'message': f'{product.title} 库存不足'})
                
                order_no = hashlib.md5(f"{user_id}{cart.product_id}{uuid.uuid4()}".encode()).hexdigest()[:16].upper()
                
                order = Order(
                    order_no=order_no,
                    user_id=user_id,
                    product_id=cart.product_id,
                    merchant_id=product.user_id,
                    quantity=cart.quantity,
                    total_price=float(product.price) * cart.quantity,
                    status='pending'
                )
                db.session.add(order)
                
                product.stock = max(0, (product.stock or 0) - cart.quantity)
                product.sales += cart.quantity
                db.session.delete(cart)
                
                orders.append({
                    'order_no': order_no,
                    'product_title': product.title,
                    'quantity': cart.quantity,
                    'total_price': float(product.price) * cart.quantity
                })
        
        elif product_id:
            # 直接购买(立即购买)
            product = Product.query.get(product_id)
            if not product or product.status != 'on_sale':
                return jsonify({'code': 400, 'message': '商品不存在或已下架'})
            if product.stock is not None and product.stock < quantity:
                return jsonify({'code': 400, 'message': '库存不足'})
            
            order_no = hashlib.md5(f"{user_id}{product_id}{uuid.uuid4()}".encode()).hexdigest()[:16].upper()
            
            order = Order(
                order_no=order_no,
                user_id=user_id,
                product_id=product_id,
                merchant_id=product.user_id,
                quantity=quantity,
                total_price=float(product.price) * quantity,
                status='pending'
            )
            db.session.add(order)
            
            product.stock = max(0, (product.stock or 0) - quantity)
            product.sales += quantity
            
            orders.append({
                'order_no': order_no,
                'product_title': product.title,
                'quantity': quantity,
                'total_price': float(product.price) * quantity
            })
        
        else:
            return jsonify({'code': 400, 'message': '请提供 cart_ids 或 product_id'})
        
        db.session.commit()
        return jsonify({'code': 200, 'message': '订单创建成功', 'data': orders})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """获取用户订单"""
    try:
        user_id = request.args.get('user_id', type=int)
        status = request.args.get('status')
        if not user_id:
            return jsonify({'code': 400, 'message': 'user_id 参数缺失'})
        
        query = db.session.query(Order, Product, User).outerjoin(
            Product, Order.product_id == Product.id
        ).outerjoin(
            User, Order.merchant_id == User.id
        ).filter(Order.user_id == user_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        orders = query.order_by(Order.created_at.desc()).all()
        
        result = []
        for order, product, merchant in orders:
            merchant_payload = None
            if merchant:
                merchant_payload = {
                    'id': merchant.id,
                    'username': merchant.username,
                    'real_name': merchant.real_name,
                    'student_id': merchant.student_id,
                    'phone': merchant.phone,
                    'email': merchant.email,
                    'address': merchant.address,
                    'role': merchant.role,
                    'status': merchant.status,
                }
            
            # 处理商品已被删除的情况
            product_title = product.title if product else '商品已删除'
            price = float(product.price) if product else 0.0
            image = first_image_url(product.images) if product else None
            
            result.append({
                'id': order.id,
                'order_no': order.order_no,
                'product_id': order.product_id,
                'product_title': product_title,
                'price': price,
                'quantity': order.quantity,
                'total_price': float(order.total_price),
                'status': order.status,
                'receiver_name': order.receiver_name,
                'receiver_phone': order.receiver_phone,
                'receiver_address': order.receiver_address,
                'payment_method': order.payment_method,
                'merchant_id': order.merchant_id,
                'merchant': merchant_payload,
                'image': image,
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else None
            })
        
        return jsonify({'code': 200, 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/order/<int:id>', methods=['GET'])
def get_order(id):
    """获取订单详情"""
    try:
        order = db.session.query(Order, Product, User).outerjoin(
            Product, Order.product_id == Product.id
        ).outerjoin(
            User, Order.merchant_id == User.id
        ).filter(Order.id == id).first()
        
        if not order:
            return jsonify({'code': 404, 'message': '订单不存在'})
        
        order_data, product, merchant = order

        merchant_payload = None
        if merchant:
            merchant_payload = {
                'id': merchant.id,
                'username': merchant.username,
                'real_name': merchant.real_name,
                'student_id': merchant.student_id,
                'phone': merchant.phone,
                'email': merchant.email,
                'address': merchant.address,
                'role': merchant.role,
                'status': merchant.status,
            }
        
        # 处理商品已被删除的情况
        product_title = product.title if product else '商品已删除'
        price = float(product.price) if product else 0.0
        image = first_image_url(product.images) if product else None
        
        return jsonify({'code': 200, 'data': {
            'id': order_data.id,
            'order_no': order_data.order_no,
            'product_id': order_data.product_id,
            'product_title': product_title,
            'price': price,
            'quantity': order_data.quantity,
            'total_price': float(order_data.total_price),
            'status': order_data.status,
            'receiver_name': order_data.receiver_name,
            'receiver_phone': order_data.receiver_phone,
            'receiver_address': order_data.receiver_address,
            'payment_method': order_data.payment_method,
            'merchant_id': order_data.merchant_id,
            'merchant': merchant_payload,
            'image': image,
            'created_at': order_data.created_at.strftime('%Y-%m-%d %H:%M:%S') if order_data.created_at else None
        }})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/order/<int:id>/pay', methods=['PUT'])
def pay_order(id):
    """订单付款"""
    try:
        order = Order.query.get(id)
        if not order:
            return jsonify({'code': 404, 'message': '订单不存在'})
        
        if order.status != 'pending':
            return jsonify({'code': 400, 'message': '订单状态不正确'})

        data = request.get_json(silent=True) or {}
        receiver_name = (data.get('receiver_name') or '').strip()
        receiver_phone = (data.get('receiver_phone') or '').strip()
        receiver_address = (data.get('receiver_address') or '').strip()
        payment_method = (data.get('payment_method') or '').strip()

        if not receiver_name or not receiver_phone or not receiver_address or not payment_method:
            return jsonify({'code': 400, 'message': '请填写完整的收货信息与支付方式'})

        if len(receiver_name) > 50:
            return jsonify({'code': 400, 'message': '收货人姓名过长'})
        if len(receiver_phone) > 20:
            return jsonify({'code': 400, 'message': '联系电话过长'})
        if len(receiver_address) > 500:
            return jsonify({'code': 400, 'message': '收货地址过长'})

        valid_methods = ['alipay', 'wechat', 'bank']
        if payment_method not in valid_methods:
            return jsonify({'code': 400, 'message': '支付方式不正确'})

        order.receiver_name = receiver_name
        order.receiver_phone = receiver_phone
        order.receiver_address = receiver_address
        order.payment_method = payment_method
        
        order.status = 'paid'
        db.session.commit()
        return jsonify({'code': 200, 'message': '付款成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/order/<int:id>/confirm', methods=['PUT'])
def confirm_order(id):
    """确认收货"""
    try:
        order = Order.query.get(id)
        if not order:
            return jsonify({'code': 404, 'message': '订单不存在'})
        
        if order.status != 'shipped':
            return jsonify({'code': 400, 'message': '订单状态不正确'})
        
        order.status = 'completed'
        db.session.commit()
        return jsonify({'code': 200, 'message': '确认收货成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/order/<int:id>/status', methods=['PUT'])
def update_order_status(id):
    """更新订单状态"""
    try:
        order = Order.query.get(id)
        if not order:
            return jsonify({'code': 404, 'message': '订单不存在'})
        
        data = request.get_json()
        new_status = data.get('status')
        
        valid_statuses = ['pending', 'paid', 'shipped', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'code': 400, 'message': '无效的状态'})
        
        order.status = new_status
        db.session.commit()
        return jsonify({'code': 200, 'message': '状态更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

# =====================================================
# 收藏相关API
# =====================================================

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """获取用户收藏列表"""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'code': 400, 'message': 'user_id 参数缺失'})
        
        favorites = db.session.query(Favorite, Product).join(
            Product, Favorite.product_id == Product.id
        ).filter(Favorite.user_id == user_id).all()
        
        result = []
        for fav, product in favorites:
            result.append({
                'id': fav.id,
                'product_id': product.id,
                'title': product.title,
                'price': float(product.price),
                'original_price': float(product.original_price) if product.original_price else None,
                'image': first_image_url(product.images),
                'views': product.views or 0,
                'created_at': fav.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'code': 200, 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/favorite', methods=['POST'])
def add_favorite():
    """添加收藏"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        
        if not user_id or not product_id:
            return jsonify({'code': 400, 'message': '参数缺失'})
        
        # 检查是否已收藏
        existing = Favorite.query.filter_by(user_id=user_id, product_id=product_id).first()
        if existing:
            return jsonify({'code': 400, 'message': '已收藏'})
        
        favorite = Favorite(user_id=user_id, product_id=product_id)
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '收藏成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/favorites/<int:id>', methods=['DELETE'])
def delete_favorite(id):
    """删除收藏(按收藏ID)"""
    try:
        favorite = Favorite.query.get(id)
        if not favorite:
            return jsonify({'code': 404, 'message': '收藏不存在'})
        
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'code': 200, 'message': '取消收藏成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/favorite/<int:product_id>', methods=['DELETE'])
def delete_favorite_by_product(product_id):
    """删除收藏(按商品ID)"""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'code': 400, 'message': 'user_id 参数缺失'})
        
        favorite = Favorite.query.filter_by(user_id=user_id, product_id=product_id).first()
        if not favorite:
            return jsonify({'code': 404, 'message': '收藏不存在'})
        
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'code': 200, 'message': '取消收藏成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)})

# =====================================================
# 页面路由
# =====================================================

@app.route('/page/login')
def page_login():
    return render_template('login.html')

@app.route('/page/register')
def page_register():
    return render_template('register.html')

@app.route('/page/index')
def page_index():
    return render_template('index.html')

@app.route('/page/product/<int:id>')
def page_product(id):
    return render_template('product.html', product_id=id)

@app.route('/page/cart')
def page_cart():
    return render_template('cart.html')

@app.route('/page/orders')
def page_orders():
    return render_template('orders.html')

@app.route('/page/merchant/<int:id>')
def page_merchant(id):
    return render_template('merchant.html', merchant_id=id)

@app.route('/page/publish')
def page_publish():
    return render_template('publish.html')

@app.route('/page/profile')
def page_profile():
    return render_template('profile.html')

@app.route('/page/admin')
def page_admin():
    return render_template('admin.html')

@app.route('/page/admin/products')
def page_admin_products():
    return render_template('admin_products.html')

@app.route('/page/admin/categories')
def page_admin_categories():
    return render_template('admin_categories.html')

@app.route('/page/admin/users')
def page_admin_users():
    return render_template('admin_users.html')

# =====================================================
# 启动应用
# =====================================================

import webbrowser
import os
import threading
import time

def open_browser():
    """延迟2秒后打开浏览器,确保服务器已启动"""
    time.sleep(2)
    try:
        webbrowser.open('http://localhost:5000/page/index')
    except Exception as e:
        print(f'打开浏览器失败: {e}')

if __name__ == '__main__':
    # 创建数据库表(如果不存在)
    with app.app_context():
        db.create_all()
        # 检查并添加address字段
        try:
            db.session.execute(text("ALTER TABLE user ADD COLUMN address TEXT"))
            db.session.commit()
        except Exception:
            # 字段已存在,忽略错误
            db.session.rollback()
        try:
            db.session.execute(text("ALTER TABLE product ADD COLUMN stock INTEGER DEFAULT 0"))
            db.session.commit()
        except Exception:
            db.session.rollback()

        # 订单表补齐收货信息/支付方式字段
        for ddl in [
            "ALTER TABLE orders ADD COLUMN receiver_name TEXT",
            "ALTER TABLE orders ADD COLUMN receiver_phone TEXT",
            "ALTER TABLE orders ADD COLUMN receiver_address TEXT",
            "ALTER TABLE orders ADD COLUMN payment_method TEXT",
        ]:
            try:
                db.session.execute(text(ddl))
                db.session.commit()
            except Exception:
                db.session.rollback()

        try:
            seed_default_categories()
        except Exception:
            db.session.rollback()
    
    # 启动浏览器线程(守护线程,主程序退出时自动结束)
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # 启动 Flask 应用
    app.run(debug=False, port=5000, use_reloader=False)