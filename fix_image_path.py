from app import app, db, Product

with app.app_context():
    # 修复图片路径（去掉开头的斜杠）
    products = Product.query.all()
    
    for product in products:
        if product.images:
            # 去掉每个图片路径开头的斜杠
            paths = [img.strip().lstrip('/') for img in product.images.split(',')]
            product.images = ','.join(paths)
    
    db.session.commit()
    
    print('图片路径修复完成！')
    for product in products:
        print(f'{product.title}: {product.images}')
