from flask import Flask, render_template, request, redirect, url_for, flash,session
import pymysql
import re  # 导入正则表达式模块

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于闪现信息（flash）

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': "root",
    'database': 'parking_system',
    'charset': 'utf8'
}


# 创建用户表（如不存在）
def init_db():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            account VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            car_plate VARCHAR(20) NOT NULL  -- 新增车牌号字段
        )
    ''')
    conn.commit()
    conn.close()
# 在密码验证函数后添加车牌号验证函数
def is_valid_car_plate(plate):
    # 简单车牌号验证规则（支持新能源车牌）
    pattern = r'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-HJ-NP-Z][A-HJ-NP-Z0-9]{4,5}[A-HJ-NP-Z0-9挂学警港澳]$'
    return bool(re.match(pattern, plate))

# 密码验证：确保密码是11位以内的数字
def is_valid_password(password):
    return bool(re.match(r'^\d{1,11}$', password))  # 验证密码是1到11位的数字


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']

        # 密码验证
        if not is_valid_password(password):
            flash('密码必须是11位以内的数字！', 'danger')
            return render_template('login.html')

        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE account=%s AND password=%s", (account, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = user[1]  # 新增这行
            flash('登录成功！', 'success')
            return redirect(url_for('success'))  # 改为重定向到success路由
        else:
            flash('账号或密码错误！', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        account = request.form['account']
        password = request.form['password']
        car_plate = request.form['car_plate'].upper()  # 获取并统一转为大写

        # 新增车牌号验证
        if not is_valid_car_plate(car_plate):
            flash('请输入有效的车牌号（示例：京A12345）', 'danger')
            return render_template('register.html')

        if not is_valid_password(password):
            flash('密码必须是11位以内的数字！', 'danger')
            return render_template('register.html')

        try:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor()
            # 修改插入语句
            cursor.execute("INSERT INTO users (username, account, password, car_plate) VALUES (%s, %s, %s, %s)",
                           (username, account, password, car_plate))
            conn.commit()
            conn.close()
            flash('注册成功，请登录！', 'success')
            return redirect(url_for('login'))
        except pymysql.err.IntegrityError as e:
            if 'account' in str(e):
                flash('账号已存在！', 'danger')
            elif 'car_plate' in str(e):
                flash('该车牌号已注册！', 'danger')
    return render_template('register.html')

# 在原有代码基础上添加以下路由
@app.route('/success')
def success():
    username = session.get('username')  # 从session获取用户名
    return render_template('success.html', username=username)

@app.route('/reserve')
def reserve():
    return render_template('reserve.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/map')
def parking_map():
    return render_template('map.html')

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/appeal')
def appeal():
    return render_template('appeal.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

