
import sqlite3
import random
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'campus_secondhand.db')

def migrate_database():
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查rating列是否已存在
        cursor.execute("PRAGMA table_info(product)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'rating' not in columns:
            print("添加rating列...")
            cursor.execute("ALTER TABLE product ADD COLUMN rating NUMERIC(2,1) DEFAULT 5.0")
        
        if 'rating_count' not in columns:
            print("添加rating_count列...")
            cursor.execute("ALTER TABLE product ADD COLUMN rating_count INTEGER DEFAULT 0")
        
        # 为现有产品添加随机评分
        cursor.execute("SELECT id FROM product")
        product_ids = [row[0] for row in cursor.fetchall()]
        
        updated_count = 0
        for product_id in product_ids:
            rating = round(random.uniform(3.0, 5.0), 1)
            rating_count = random.randint(5, 50)
            
            cursor.execute(
                "UPDATE product SET rating = ?, rating_count = ? WHERE id = ?",
                (rating, rating_count, product_id)
            )
            updated_count += 1
        
        conn.commit()
        print(f"成功！更新了 {updated_count} 个产品的评分信息")
        
    except Exception as e:
        print(f"数据库迁移出错: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()

