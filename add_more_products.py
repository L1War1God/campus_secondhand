from app import app, db, Product

with app.app_context():
    # 添加更多商品
    products = [
        Product(
            user_id=1,
            category_id=1,
            title='iPad Air 5 256G',
            description='M1芯片，深空灰色，带原装保护套',
            price=4200.00,
            original_price=5999.00,
            condition='good',
            status='on_sale',
            views=123
        ),
        Product(
            user_id=1,
            category_id=1,
            title='MacBook Pro 14寸 M2',
            description='16GB+512GB，深空黑色，成色95新',
            price=12000.00,
            original_price=16999.00,
            condition='good',
            status='on_sale',
            views=89
        ),
        Product(
            user_id=1,
            category_id=2,
            title='Python编程从入门到实践',
            description='第二版，中文版，有少量笔记',
            price=20.00,
            original_price=69.00,
            condition='good',
            status='on_sale',
            views=156
        ),
        Product(
            user_id=1,
            category_id=2,
            title='数据结构与算法分析',
            description='C语言描述，经典教材',
            price=30.00,
            original_price=89.00,
            condition='good',
            status='on_sale',
            views=78
        ),
        Product(
            user_id=1,
            category_id=3,
            title='美的电饭煲 4L',
            description='多功能智能电饭煲，几乎全新',
            price=150.00,
            original_price=399.00,
            condition='new',
            status='on_sale',
            views=67
        ),
        Product(
            user_id=1,
            category_id=3,
            title='飞利浦剃须刀',
            description='电动三刀头，全身水洗',
            price=200.00,
            original_price=499.00,
            condition='good',
            status='on_sale',
            views=45
        ),
        Product(
            user_id=1,
            category_id=4,
            title='篮球 斯伯丁',
            description='室内外通用，手感很好',
            price=80.00,
            original_price=169.00,
            condition='good',
            status='on_sale',
            views=56
        ),
        Product(
            user_id=1,
            category_id=4,
            title='跑步鞋 李宁',
            description='赤兔5Pro，42码，穿过几次',
            price=280.00,
            original_price=499.00,
            condition='good',
            status='on_sale',
            views=78
        ),
        Product(
            user_id=1,
            category_id=5,
            title='羽绒服 波司登',
            description='中长款，黑色L码，保暖性好',
            price=350.00,
            original_price=899.00,
            condition='good',
            status='on_sale',
            views=45
        ),
        Product(
            user_id=1,
            category_id=5,
            title="牛仔裤 Levi's",
            description='经典501款，W32L32',
            price=180.00,
            original_price=599.00,
            condition='good',
            status='on_sale',
            views=67
        ),
        Product(
            user_id=1,
            category_id=1,
            title='华为Mate 60 Pro',
            description='12GB+512GB，雅川青，成色很新',
            price=5800.00,
            original_price=6999.00,
            condition='good',
            status='on_sale',
            views=234
        ),
        Product(
            user_id=1,
            category_id=3,
            title='索尼耳机 WH-1000XM4',
            description='无线降噪耳机，黑色',
            price=1500.00,
            original_price=2499.00,
            condition='good',
            status='on_sale',
            views=89
        ),
    ]
    db.session.add_all(products)
    db.session.commit()
    
    total = Product.query.filter_by(status='on_sale').count()
    print(f'已添加 {len(products)} 个商品')
    print(f'当前共有 {total} 个在售商品')
