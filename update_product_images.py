from app import app, db, Product

with app.app_context():
    # 更新商品图片
    products = Product.query.all()
    
    for product in products:
        if product.title == '九成新高数教材':
            product.images = '/static/picture/gaodengshuxue.png'
        elif product.title == 'MacBook Pro 2020':
            product.images = '/static/picture/MacBook_Pro_2020.png'
        elif product.title == '宿舍小风扇':
            product.images = '/static/picture/宿舍小风扇.png'
        elif product.title == '索尼WH-1000XM4':
            product.images = '/static/picture/索尼WH-1000XM4.png'
        elif product.title == '台灯':
            product.images = '/static/picture/台灯.png'
    
    db.session.commit()
    
    print('商品图片更新完成！')
    for product in products:
        print(f'{product.title}: {product.images}')
