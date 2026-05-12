
from app import app, db, Product
import random

def migrate_ratings():
    with app.app_context():
        # 检查是否已有rating列（SQLite特定）
        try:
            # 尝试查询rating字段
            test_product = Product.query.first()
            if test_product:
                # 检查是否有rating属性
                if hasattr(test_product, 'rating'):
                    print("Rating字段已存在，更新现有产品...")
                else:
                    print("需要添加rating和rating_count字段...")
        except Exception as e:
            print(f"检查现有字段时出错: {e}")
        
        # 更新所有产品，添加默认评分
        products = Product.query.all()
        updated_count = 0
        
        for product in products:
            # 为每个产品生成随机评分（3.0-5.0之间）
            if not hasattr(product, 'rating') or product.rating is None:
                product.rating = round(random.uniform(3.0, 5.0), 1)
            if not hasattr(product, 'rating_count') or product.rating_count is None:
                product.rating_count = random.randint(5, 50)
            updated_count += 1
        
        try:
            db.session.commit()
            print(f"成功更新 {updated_count} 个产品的评分信息")
        except Exception as e:
            db.session.rollback()
            print(f"提交数据库更改时出错: {e}")
            print("正在尝试更安全的方式添加字段...")
            
            # 如果上面失败，尝试使用原始SQL（SQLite特定）
            try:
                # 对于SQLite ALTER TABLE添加列
                db.session.execute(text('ALTER TABLE product ADD COLUMN rating NUMERIC(2,1) DEFAULT 5.0'))
                db.session.execute(text('ALTER TABLE product ADD COLUMN rating_count INTEGER DEFAULT 0'))
                db.session.commit()
                
                # 再次更新产品评分
                products = Product.query.all()
                for product in products:
                    product.rating = round(random.uniform(3.0, 5.0), 1)
                    product.rating_count = random.randint(5, 50)
                
                db.session.commit()
                print(f"成功添加评分字段并更新 {len(products)} 个产品")
            except Exception as e2:
                db.session.rollback()
                print(f"原始SQL方式也失败: {e2}")
                print("请检查数据库结构或重新创建数据库")

if __name__ == "__main__":
    migrate_ratings()

