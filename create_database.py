import sqlite3
import csv
import os

def create_tables():
    with sqlite3.connect('individual_by_hand.db') as conn:
        cursor = conn.cursor()
        # Products 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cartegory TEXT NOT NULL,
                model TEXT NOT NULL,
                name TEXT NOT NULL,
                leather TEXT,
                country TEXT,
                size TEXT,
                explantion TEXT,
                price INTEGER NOT NULL
            )
        ''')
        # Images 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES Products (id)
            )
        ''')
        # Orders 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                total_price INTEGER NOT NULL,
                FOREIGN KEY (product_id) REFERENCES Products (id)
            )
        ''')
        conn.commit()

def insert_products_from_csv(csv_file_path):
    with sqlite3.connect('individual_by_hand.db') as conn:
        cursor = conn.cursor()
        with open(csv_file_path, 'r', encoding='cp949') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                cursor.execute('''
                    INSERT INTO Products (cartegory, model, name, leather, country, size, explantion, price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['cartegory'],
                    row['model'],
                    row['name'],
                    row['leather'],
                    row['country'],
                    row['size'],
                    row['explantion'],
                    int(row['price']) if row['price'] else None
                ))
        conn.commit()

def insert_images(image_directory):
    with sqlite3.connect('individual_by_hand.db') as conn:
        cursor = conn.cursor()
        # Products 테이블에서 모델-아이디 매핑 가져오기
        cursor.execute('SELECT model, id FROM Products')
        product_model_map = {row[0]: row[1] for row in cursor.fetchall()}

        for filename in os.listdir(image_directory):
            model = filename.split(' ')[0].replace('_', '-')  # 파일명에서 모델 번호 추출
            if model in product_model_map:
                image_path = os.path.join(image_directory, filename)

                # 중복 여부 확인
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM Images 
                    WHERE product_id = ? AND image_path = ?
                ''', (product_model_map[model], image_path))

                if cursor.fetchone()[0] == 0:  # 중복되지 않은 경우에만 삽입
                    cursor.execute('''
                        INSERT INTO Images (product_id, image_path)
                        VALUES (?, ?)
                    ''', (product_model_map[model], image_path))
        conn.commit()


if __name__ == '__main__':
    # 데이터베이스 초기화
    create_tables()
    # CSV 경로와 이미지 경로 설정
    csv_file_path = 'products.csv'  # 제품 데이터 CSV 파일 경로
    image_directory = 'static/images'  # 이미지 파일 경로
    # 제품 데이터 삽입
    insert_products_from_csv(csv_file_path)
    # 이미지 데이터 삽입
    insert_images(image_directory)
