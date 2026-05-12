from app import app, db, User, Product, Category, Order, Cart, Favorite

with app.app_context():
    # 删除所有表
    db.drop_all()
    # 创建所有表
    db.create_all()
    
    # 创建测试用户
    test_user = User(
        username='testuser',
        password='5f4dcc3b5aa765d61d8327deb882cf99',  # md5('password')
        real_name='测试用户',
        phone='13800138000',
        email='test@example.com',
        address='测试地址'
    )
    db.session.add(test_user)
    db.session.commit()
    
    print('数据库初始化完成！')
    print(f'创建了测试用户: {test_user.username}')
