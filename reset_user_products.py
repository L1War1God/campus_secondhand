from app import app, db, Product

with app.app_context():
    # 将普通用户(zhangsan, user_id=2)发布的商品转移到商家(lisi, user_id=3)
    products = Product.query.filter_by(user_id=2).all()
    
    print(f'找到 {len(products)} 个属于普通用户(zhangsan)的商品')
    
    for product in products:
        print(f'转移商品: {product.title} (ID: {product.id})')
        product.user_id = 3  # 转移到商家lisi
    
    db.session.commit()
    
    # 验证结果
    zhangsan_products = Product.query.filter_by(user_id=2).count()
    lisi_products = Product.query.filter_by(user_id=3).count()
    
    print(f'\n修改完成！')
    print(f'普通用户(zhangsan)的商品数量: {zhangsan_products}')
    print(f'商家(lisi)的商品数量: {lisi_products}')
