import sqlite3

# 데이터베이스 파일명
DB_NAME = "individual_by_hand.db"

# Contact 테이블 생성 함수
def create_contact_table():
    try:
        # 데이터베이스 연결
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Contact 테이블 생성 SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS Contact (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # SQL 실행
        cursor.execute(create_table_sql)
        conn.commit()
        print("Contact 테이블이 성공적으로 생성되었습니다.")

    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
    finally:
        # 연결 종료
        if conn:
            conn.close()

# 메인 실행
if __name__ == "__main__":
    create_contact_table()
