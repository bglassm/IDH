import sqlite3
import os

def check_missing_images(image_directory):
    # 이미지 디렉토리 내 파일 목록 가져오기
    directory_files = set(os.listdir(image_directory))
    
    # 데이터베이스에서 저장된 이미지 파일명 가져오기
    with sqlite3.connect('individual_by_hand.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT image_path FROM Images')
        db_files = {os.path.basename(row[0]) for row in cursor.fetchall()}
    
    # 누락된 파일 찾기
    missing_files = directory_files - db_files
    extra_files = db_files - directory_files

    if missing_files:
        print("누락된 파일:")
        for file in missing_files:
            print(file)
    else:
        print("누락된 파일 없음.")
    
    if extra_files:
        print("\n데이터베이스에 있지만 디렉토리에 없는 파일:")
        for file in extra_files:
            print(file)
    else:
        print("\n디렉토리에 없는 파일 없음.")

# 이미지 디렉토리 경로 지정
image_directory = "static/images"
check_missing_images(image_directory)
