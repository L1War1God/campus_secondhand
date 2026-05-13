from app import app, db, Category, User, Product

with app.app_context():
    # 删除所有表
    db.drop_all()
    # 创建所有表
    db.create_all()
    
    # 插入分类数据
    categories = [
        Category(name='数码产品', parent_id=0, sort_order=1, status=1),
        Category(name='书籍教材', parent_id=0, sort_order=2, status=1),
        Category(name='生活用品', parent_id=0, sort_order=3, status=1),
        Category(name='服饰鞋包', parent_id=0, sort_order=4, status=1),
        Category(name='运动户外', parent_id=0, sort_order=5, status=1),
        Category(name='其他', parent_id=0, sort_order=99, status=1),
        Category(name='手机', parent_id=1, sort_order=1, status=1),
        Category(name='电脑', parent_id=1, sort_order=2, status=1),
        Category(name='耳机', parent_id=1, sort_order=3, status=1),
        Category(name='教材教辅', parent_id=2, sort_order=1, status=1),
        Category(name='小说文学', parent_id=2, sort_order=2, status=1),
        Category(name='宿舍用品', parent_id=3, sort_order=1, status=1),
        Category(name='小电器', parent_id=3, sort_order=2, status=1),
    ]
    db.session.add_all(categories)
    db.session.commit()
    
    # 插入用户数据（密码: 123456 MD5）
    users = [
        User(username='admin', password='e10adc3949ba59abbe56e057f20f883e', 
             real_name='管理员', student_id='20230001', phone='13800000000', 
             email='admin@campus.com', role='admin', status='active'),
        User(username='zhangsan', password='e10adc3949ba59abbe56e057f20f883e', 
             real_name='张三', student_id='20230002', phone='13900000001', 
             email='zhangsan@campus.com', role='user', status='active'),
        User(username='lisi', password='e10adc3949ba59abbe56e057f20f883e', 
             real_name='李四', student_id='20230003', phone='13900000002', 
             email='lisi@campus.com', role='merchant', status='active'),
    ]
    db.session.add_all(users)
    db.session.commit()
    
    # 插入商品数据
    products = [
        Product(user_id=2, category_id=8, title='九成新高数教材', 
                description='高等数学第七版上册，几乎全新，无笔记', 
                price=25.00, condition='like_new', status='on_sale'),
        Product(user_id=2, category_id=9, title='MacBook Pro 2020', 
                description='13寸，i5，8+256，无维修', 
                price=4500.00, condition='good', status='on_sale'),
        Product(user_id=3, category_id=12, title='宿舍小风扇', 
                description='USB充电，三档调节，很安静', 
                price=35.00, condition='like_new', status='on_sale'),
        Product(user_id=2, category_id=10, title='索尼WH-1000XM4', 
                description='降噪耳机，九成新，包装齐全', 
                price=1200.00, condition='like_new', status='on_sale'),
        Product(user_id=3, category_id=13, title='台灯', 
                description='LED护眼台灯，三档色温', 
                price=45.00, condition='good', status='on_sale'),
    ]
    db.session.add_all(products)
    db.session.commit()
    
    print('数据库初始化完成！')
    print(f'创建了 {len(categories)} 个分类')
    print(f'创建了 {len(users)} 个用户')
    print(f'创建了 {len(products)} 个商品')
