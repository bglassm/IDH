from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('main.html')

# 카테고리 페이지 경로 추가
@app.route('/category/<category_name>')
def category_page(category_name):
    # 예시로 빈 페이지를 렌더링. 이후에 이 부분에 카테고리별 로직을 추가할 수 있습니다.
    return render_template('category.html', category_name=category_name)

if __name__ == '__main__':
    app.run(debug=True)