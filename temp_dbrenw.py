import sqlite3

# 데이터베이스 파일
db_name = 'individual_by_hand.db'

# 데이터베이스 연결
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

try:
    # 1. 기존 테이블 구조 확인
    cursor.execute("PRAGMA table_info(Products)")
    columns = cursor.fetchall()
    print("Before Update - Table Structure:")
    for col in columns:
        print(col)

    # 2. 새 테이블 생성 (올바른 컬럼명으로 수정)
    cursor.execute('''
        CREATE TABLE Products_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            model TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT, -- 컬럼명 수정 (cartegory -> category)
            size TEXT,
            leather TEXT,
            explanation TEXT
        )
    ''')

    # 3. 기존 데이터 복사
    cursor.execute('''
        INSERT INTO Products_new (id, name, model, price, category, size, leather, explanation)
        SELECT id, name, model, price, cartegory, size, leather, explanation
        FROM Products
    ''')

    # 4. 기존 테이블 삭제
    cursor.execute("DROP TABLE Products")

    # 5. 새 테이블의 이름을 원래 테이블명으로 변경
    cursor.execute("ALTER TABLE Products_new RENAME TO Products")

    # 6. 테이블 구조 확인
    cursor.execute("PRAGMA table_info(Products)")
    columns = cursor.fetchall()
    print("After Update - Table Structure:")
    for col in columns:
        print(col)

    # 변경사항 저장
    conn.commit()
    print("Table column name updated successfully!")

except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

finally:
    # 데이터베이스 연결 종료
    conn.close()
