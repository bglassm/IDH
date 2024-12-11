import sqlite3

def fix_none_image_paths():
    conn = sqlite3.connect('individual_by_hand.db')
    cursor = conn.cursor()

    # image_path가 NULL인 경우 default.png로 설정
    cursor.execute("""
        UPDATE Images
        SET image_path = 'images/default.png'
        WHERE image_path IS NULL
    """)
    conn.commit()
    conn.close()
    print("None image paths updated successfully.")

fix_none_image_paths()
