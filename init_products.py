from app import app, db, Product, Category

with app.app_context():
    # 创建商品分类
    categories = [
        Category(name='数码电子', parent_id=0, sort_order=1, status=1),
        Category(name='图书教材', parent_id=0, sort_order=2, status=1),
        Category(name='生活用品', parent_id=0, sort_order=3, status=1),
        Category(name='运动户外', parent_id=0, sort_order=4, status=1),
        Category(name='服装鞋帽', parent_id=0, sort_order=5, status=1),
    ]
    db.session.add_all(categories)
    db.session.commit()
    
    # 创建测试商品
    products = [
        Product(
            user_id=1,
            category_id=2,
            title='九成新高数教材',
            description='同济大学高等数学第七版，上下册，无笔记划线',
            price=25.00,
            original_price=98.00,
            condition='good',
            status='on_sale',
            views=156
        ),
        Product(
            user_id=1,
            category_id=1,
            title='iPhone 13 128G 蓝色',
            description='使用一年，电池健康度89%，无划痕',
            price=3500.00,
            original_price=5999.00,
            condition='good',
            status='on_sale',
            views=234
        ),
        Product(
            user_id=1,
            category_id=3,
            title='宜家书架',
            description='白色四层书架，尺寸80x30x120cm',
            price=80.00,
            original_price=199.00,
            condition='good',
            status='on_sale',
            views=89
        ),
        Product(
            user_id=1,
            category_id=4,
            title='羽毛球拍 尤尼克斯',
            description='NR-D11型号，几乎全新，送球和手胶',
            price=120.00,
            original_price=299.00,
            condition='new',
            status='on_sale',
            views=67
        ),
        Product(
            user_id=1,
            category_id=5,
            title='Nike Air Force 1 白色 42码',
            description='穿过几次，成色很新，正品保证',
            price=450.00,
            original_price=799.00,
            condition='good',
            status='on_sale',
            views=145
        ),
        Product(
            user_id=1,
            category_id=2,
            title='线性代数及其应用',
            description='第五版，英文原版，适合双语教学',
            price=35.00,
            original_price=128.00,
            condition='good',
            status='on_sale',
            views=45
        ),
        Product(
            user_id=1,
            category_id=1,
            title='AirPods Pro 第二代',
            description='带MagSafe充电盒，使用半年',
            price=1200.00,
            original_price=1899.00,
            condition='good',
            status='on_sale',
            views=178
        ),
        Product(
            user_id=1,
            category_id=3,
            title='小米台灯Pro',
            description='护眼台灯，可调色温亮度',
            price=150.00,
            original_price=299.00,
            condition='good',
            status='on_sale',
            views=98
        ),
    ]
    db.session.add_all(products)
    db.session.commit()
    
    print('商品数据初始化完成！')
    print(f'创建了 {len(categories)} 个分类')
    print(f'创建了 {len(products)} 个商品')
