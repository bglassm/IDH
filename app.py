import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, flash, redirect, url_for
import sqlite3
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Flask 메시지 활성화

# 데이터베이스 연결 함수
def get_db_connection():
    conn = sqlite3.connect('individual_by_hand.db')
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형태로 반환
    return conn

# Gmail SMTP 설정
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")  # Gmail 주소
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")  # Gmail 앱 비밀번호

# Gmail을 이용해 메일 전송 함수
def send_email(to_email, subject, body):
    try:
        # 이메일 생성
        msg = MIMEMultipart()
        msg['From'] = GMAIL_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        # 메일 본문 설정
        msg.attach(MIMEText(body, 'plain'))

        # Gmail SMTP 서버 연결 및 메일 전송
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
            server.sendmail(GMAIL_EMAIL, to_email, msg.as_string())

        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")

# Contact 제출 처리
@app.route('/contact_submit', methods=['POST'])
def contact_submit():
    if request.method == 'POST':
        data = request.form

        # 입력 데이터 검증
        required_fields = ['first_name', 'last_name', 'email', 'message']
        for field in required_fields:
            if not data.get(field) or data.get(field).strip() == '':
                flash(f"{field.replace('_', ' ').title()} is required.", "error")
                return redirect(url_for('home') + "#contact")

        # 이메일 검증
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, data['email']):
            flash("유효한 이메일 주소를 입력해주세요.", "error")
            return redirect(url_for('home') + "#contact")

        # 데이터베이스 저장
        conn = get_db_connection()
        try:
            conn.execute(
                '''
                INSERT INTO Contact (first_name, last_name, email, message)
                VALUES (?, ?, ?, ?)
                ''',
                (data['first_name'], data['last_name'], data['email'], data['message'])
            )
            conn.commit()
        except Exception as e:
            flash("메시지 전송 중 오류가 발생했습니다. 다시 시도해주세요.", "error")
            return redirect(url_for('home') + "#contact")
        finally:
            conn.close()

        # 이메일 전송 (Gmail SMTP)
        admin_email_body = f"""
        새로운 문의가 접수되었습니다:

        - 이름: {data['first_name']} {data['last_name']}
        - 이메일: {data['email']}
        - 메시지:
        {data['message']}
        """
        try:
            send_email('individualbyhand@gmail.com', "New Contact Form Submission", admin_email_body)
            flash("메시지가 성공적으로 전송되었습니다! 빠른 시일 내에 답변드리겠습니다.", "success")
        except Exception as e:
            flash(f"메일 전송에 실패했습니다: {str(e)}", "error")
            return redirect(url_for('home') + "#contact")

        # 성공 시 Contact 섹션으로 리디렉션
        return redirect(url_for('home') + "#contact")

# 특정 카테고리의 제품을 렌더링
@app.route('/products/<category>')
def show_products(category='all'):
    conn = get_db_connection()
    default_image = 'images/default.png'

    query = '''
        SELECT DISTINCT
            products.id,
            products.name,
            products.model,
            products.price,
            COALESCE(
                (SELECT REPLACE(image_path, 'static/', '') FROM Images WHERE product_id = products.id AND image_path LIKE '%(1)%' LIMIT 1),
                ?
            ) AS image_path
        FROM Products
    '''
    if category != 'all':
        query += 'WHERE products.cartegory = ?'

    params = (default_image,) if category == 'all' else (default_image, category)
    products = conn.execute(query, params).fetchall()
    conn.close()

    category_title = "All Products" if category == 'all' else str(category).title()
    return render_template('products.html', products=products, category=category_title)

# 제품 상세 페이지
@app.route('/product/<model>')
def product_page(model):
    conn = get_db_connection()
    product = conn.execute('''
        SELECT products.name, products.model, products.price, products.size, products.leather,
               products.explanation AS explanation, GROUP_CONCAT(Images.image_path) AS images
        FROM products
        LEFT JOIN Images ON products.id = Images.product_id
        WHERE products.model = ? COLLATE NOCASE
        GROUP BY products.id
    ''', (model,)).fetchone()
    conn.close()

    if product:
        images = product["images"].split(",") if product["images"] else ["static/images/default.png"]
        product_data = {
            "name": product["name"],
            "model": product["model"],
            "price": "{:,}원".format(product["price"]),
            "size": product["size"] or "N/A",
            "leather": product["leather"] or "N/A",
            "description": product["explanation"] or "No description available.",
            "images": images
        }
        return render_template('product.html', product=product_data)
    else:
        return "Product not found", 404

# 주문 페이지
@app.route('/order/<model>', methods=['GET', 'POST'])
def order_page(model):
    conn = get_db_connection()
    product = conn.execute('''
        SELECT products.name, products.model, products.price,
               COALESCE(
                   (SELECT REPLACE(image_path, 'static/', '') FROM Images WHERE product_id = products.id AND image_path LIKE '%(1)%' LIMIT 1),
                   'images/default.png'
               ) AS image_path
        FROM products
        WHERE model = ? COLLATE NOCASE
    ''', (model,)).fetchone()
    conn.close()

    if not product:
        return "Product not found", 404

    product_data = {
        "name": product["name"],
        "model": product["model"],
        "price": "{:,}원".format(product["price"]),
        "image_path": product["image_path"]
    }

    return render_template('order.html', product=product_data)

# 주문 처리 및 이메일 전송
@app.route('/submit_order', methods=['POST'])
def submit_order():
    data = request.form

    # 입력 데이터 검증
    required_fields = ['user_description', 'size', 'name', 'phone', 'email']
    for field in required_fields:
        if not data.get(field) or data.get(field).strip() == '':
            flash(f"{field} is required.", "error")
            return redirect(request.referrer)

    # 전화번호와 이메일 검증
    phone_pattern = r"^\d{3}-\d{3,4}-\d{4}$"
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(phone_pattern, data['phone']):
        flash("Invalid phone number format. Use XXX-XXXX-XXXX.", "error")
        return redirect(request.referrer)
    if not re.match(email_pattern, data['email']):
        flash("Invalid email address.", "error")
        return redirect(request.referrer)

    # 데이터베이스 저장
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO Orders (product_id, user_description, size, color, shape, leather, additional_requests, name, phone, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                data['product_id'], data['user_description'], data['size'], data.get('color'),
                data.get('shape'), data.get('leather'), data.get('additional_requests'),
                data['name'], data['phone'], data['email']
            )
        )
        order_id = cursor.lastrowid  # 방금 삽입된 주문 ID 가져오기
        conn.commit()
    except Exception as e:
        flash("Error saving order. Please try again later.", "error")
        return redirect(request.referrer)
    finally:
        conn.close()

    # 주문번호 생성
    created_at = datetime.now().strftime('%Y%m%d')  # 날짜: YYYYMMDD 형식
    order_number = f"{created_at}815{order_id}"

    # 제작자에게 전송할 이메일 내용
    admin_email_body = f"""
    새로운 주문이 접수되었습니다:

    - 주문번호: {order_number}
    - 이름: {data['name']}
    - 전화번호: {data['phone']}
    - 이메일: {data['email']}
    - 사용자 설명: {data['user_description']}
    - 크기: {data['size']}
    - 색상: {data.get('color', 'N/A')}
    - 형태: {data.get('shape', 'N/A')}
    - 가죽: {data.get('leather', 'N/A')}
    - 추가 요청사항: {data.get('additional_requests', 'N/A')}
    """

    # 주문자에게 전송할 이메일 내용
    customer_email_body = f"""
    감사합니다! 주문이 접수되었습니다.

    고객님의 주문 정보는 다음과 같습니다:
    - 주문번호: {order_number}
    - 사용자 설명: {data['user_description']}
    - 크기: {data['size']}
    - 색상: {data.get('color', 'N/A')}
    - 형태: {data.get('shape', 'N/A')}
    - 가죽: {data.get('leather', 'N/A')}
    - 추가 요청사항: {data.get('additional_requests', 'N/A')}

    Thank you! Your order has been received.

    Below is your order information:
    - Order Number: {order_number}
    - User Description: {data['user_description']}
    - Size: {data['size']}
    - Color: {data.get('color', 'N/A')}
    - Shape: {data.get('shape', 'N/A')}
    - Leather: {data.get('leather', 'N/A')}
    - Additional Requests: {data.get('additional_requests', 'N/A')}
    """

    # 이메일 전송
    send_email('individualbyhand@gmail.com', "New Order Received", admin_email_body)
    send_email(data['email'], "Order Confirmation", customer_email_body)

    # 주문 완료 페이지로 리디렉션
    return render_template(
        'order_success.html',
        name=data['name'],
        order_number=order_number,
        phone=data['phone'],
        email=data['email']
    )

# 메인 페이지
@app.route('/')
def home():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)
