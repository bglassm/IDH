import sqlite3

conn = sqlite3.connect('individual_by_hand.db')
cursor = conn.cursor()

# 중복된 이미지 확인
cursor.execute('''
    SELECT image_path, COUNT(*)
    FROM Images
    GROUP BY image_path
    HAVING COUNT(*) > 1
''')

duplicates = cursor.fetchall()
if duplicates:
    print("중복된 이미지 경로:")
    for duplicate in duplicates:
        print(duplicate)
else:
    print("중복 데이터 없음.")

conn.close()
