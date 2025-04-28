from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import re  # 导入正则表达式模块

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于闪现信息（flash）

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': "123456",
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
            password VARCHAR(255) NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()


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
            flash('登录成功！', 'success')
            return render_template('success.html', username=user[1])
        else:
            flash('账号或密码错误！', 'danger')
    return render_template('login.html')

@app.route('/login_1', methods=['GET', 'POST'])
def login_1():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        # 密码验证
        if not is_valid_password(password):
            flash('密码必须是11位以内的数字！', 'danger')
            return render_template('login_1.html')
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE account=%s AND password=%s", (account, password))
        manager = cursor.fetchone()
        conn.close()
        if manager:
            flash('登录成功！', 'sucess')
            if manager[0]=='19533733731':
                return render_template('manage1.html')
            elif manager[0]=='19533733732':
                return render_template('manage2.html')
        else:
            flash('账号或密码错误！', 'danger')
    return render_template('login_1.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        account = request.form['account']
        password = request.form['password']
        # 密码验证
        if not is_valid_password(password):
            flash('密码必须是11位以内的数字！', 'danger')
            return render_template('register.html')
        try:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, account, password) VALUES (%s, %s, %s)",
                           (username, account, password))
            conn.commit()
            conn.close()
            flash('注册成功，请登录！', 'success')
            return redirect(url_for('login'))
        except pymysql.err.IntegrityError:
            flash('账号已存在！', 'danger')
    return render_template('register.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
