import sqlite3

def update_category():
    db_path = "individual_by_hand.db"  # 데이터베이스 경로를 설정하세요.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 카테고리를 Bag에서 bags로 업데이트
        cursor.execute("UPDATE Products SET cartegory = 'bags' WHERE cartegory = 'Bag';")
        conn.commit()
        print("카테고리가 'Bag'에서 'bags'로 성공적으로 변경되었습니다.")

        # 변경 결과 확인
        cursor.execute("SELECT DISTINCT cartegory FROM Products;")
        categories = cursor.fetchall()
        print("현재 카테고리 목록:")
        for category in categories:
            print(category[0])

    except sqlite3.Error as e:
        print(f"데이터베이스 오류가 발생했습니다: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_category()
