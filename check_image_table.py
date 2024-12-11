import sqlite3

# 데이터베이스 연결
conn = sqlite3.connect('individual_by_hand.db')
cursor = conn.cursor()

# Images 테이블 데이터 확인
cursor.execute("SELECT * FROM Images;")
images = cursor.fetchall()

with open("images_output.txt", "w", encoding="utf-8") as f:
    for row in cursor.execute("SELECT * FROM Images"):
        f.write(str(row) + "\n")

# 닫기
conn.close()