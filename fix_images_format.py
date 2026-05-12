from app import app, db, Product
import json

with app.app_context():
    # 更新商品图片为逗号分隔格式
    products = Product.query.all()
    
    for product in products:
        if product.images:
            if product.images.startswith('['):
                # 如果是JSON数组格式，转换为逗号分隔格式
                try:
                    img_list = json.loads(product.images)
                    product.images = ','.join(img_list)
                except:
                    # 如果解析失败，保持原样
                    pass
    
    db.session.commit()
    
    print('商品图片格式修复完成！')
    for product in products:
        print(f'{product.title}: {product.images}')
