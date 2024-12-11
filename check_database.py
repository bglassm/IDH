import sqlite3

# 데이터베이스 연결
conn = sqlite3.connect('individual_by_hand.db')
cursor = conn.cursor()

# 테이블 확인
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("생성된 테이블 목록:")
for table in tables:
    print(table[0])

# 닫기
conn.close()


