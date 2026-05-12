from app import app, db, Product
import json

with app.app_context():
    # 更新商品图片为数组格式
    products = Product.query.all()
    
    for product in products:
        if product.images and isinstance(product.images, str) and not product.images.startswith('['):
            # 如果是字符串格式，转换为数组格式的JSON字符串
            product.images = json.dumps([product.images])
    
    db.session.commit()
    
    print('商品图片格式更新完成！')
    for product in products:
        print(f'{product.title}: {product.images}')
