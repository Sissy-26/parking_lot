from flask import Flask, render_template, request, redirect, url_for, flash,session,jsonify
import pymysql
import re  # 导入正则表达式模块
#新添mxy--------------------------------------------------
import datetime 
#新添mxy--------------------------------------------------
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
            if manager[2]=='manager1':
                return redirect(url_for('manage1'))
            elif manager[2]=='manager2':
                return render_template('manage2')
        else:
            flash('账号或密码错误！', 'danger')
    return render_template('login_1.html')

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

#新添mxy--------------------------------------------------
@app.route('/blacklist',methods=['GET'])
def blacklist():
    if request.method=="GET":
        conn = pymysql.connect(**DB_CONFIG)
        cursor=conn.cursor()
        cursor.execute("select car_plate,time,reason from blacklist")
        data=cursor.fetchall()
        temp={}
        result=[]
        if data!=None:
            for i in data:
                temp['car_plate']=i[0]
                temp['time']=i[1]
                temp['reason']=i[2]
                result.append(temp.copy())
            return jsonify(result)
        else:
            return jsonify([])
        
@app.route('/users',methods=['GET'])
def users():
    if request.method=="GET":
        conn = pymysql.connect(**DB_CONFIG)
        cursor=conn.cursor()
        cursor.execute("select account,car_plate,member from users where account != 'manager1' and account != 'manager2' ")
        data=cursor.fetchall()
        temp={}
        result=[]
        if data!=None:
            for i in data:
                temp['account']=i[0]
                temp['car_plate']=i[1]
                temp['member']=i[2]
                result.append(temp.copy())
            return jsonify(result)
        else:
            return jsonify([])
        
@app.route('/blacklist_add',methods=['POST'])
def blacklist_add():
    if request.method=="POST":
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reason=request.form['reason']
        car_plate = request.form['car_plate'].upper()  # 获取并统一转为大写
        try:
            conn = pymysql.connect(**DB_CONFIG)
            cursor=conn.cursor()   
            cursor.execute("INSERT INTO blacklist (car_plate, time, reason) VALUES (%s, %s, %s)",
                           (car_plate, time, reason))
            conn.commit()
            conn.close()
            return "1"
        except pymysql.err.IntegrityError as e:
            if car_plate in str(e):
                return "2"
    flash('error', 'danger')
    return "0"

@app.route('/user_add', methods=['GET', 'POST'])
def user_add():
    if request.method == 'POST':
        username = request.form['username']
        account = request.form['account']
        password = request.form['password']
        car_plate = request.form['car_plate'].upper()  # 获取并统一转为大写
        member = request.form['member']

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
            cursor.execute("INSERT INTO users (username, account, password, car_plate, member) VALUES (%s, %s, %s, %s,%s)",
                           (username, account, password, car_plate,member))
            conn.commit()
            conn.close()
            return "1"
        except pymysql.err.IntegrityError as e:
            if account in str(e):
                return "2"
    return "0"   

@app.route('/manage1', methods=['GET', 'POST'])
def manage1():    
    return render_template('manage1.html')  


@app.route('/manage2', methods=['GET', 'POST'])
def manage2(): 
    return render_template('manage2.html')

@app.route('/user_delete', methods=['GET', 'POST'])
def user_delete(): 
    if request.method == 'POST':
        account = request.form['account']
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        if cursor.execute("SELECT * FROM users WHERE account=%s", (account)):
            cursor.execute("delete from users  where account= \'"+str(account)+"\'");
            conn.commit()
            return "1"
        else:
            return "2"
    return "0"     
    

@app.route('/blacklist_delete', methods=['GET', 'POST'])
def blacklist_delete(): 
    if request.method == 'POST':
        car_plate = request.form['car_plate']
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        if cursor.execute("SELECT * FROM blacklist WHERE car_plate=%s", (car_plate)):
            cursor.execute("delete from blacklist  where car_plate= \'"+str(car_plate)+"\'");
            conn.commit()
            return "1"
        else:
            return "2"
    return "0"


@app.route('/member_delete', methods=['GET', 'POST'])
def member_delete(): 
    if request.method == 'POST':
        account = request.form['account']
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        if cursor.execute("SELECT * FROM users WHERE account=%s", (account)):
            cursor.execute("update users set member=\'否\' where account= \'"+str(account)+"\'");
            conn.commit()
            return "1"
        else:
            return "2"
    return "0"

@app.route('/member_add', methods=['GET', 'POST'])
def member_add(): 
    if request.method == 'POST':
        account = request.form['account']
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        if cursor.execute("SELECT * FROM users WHERE account=%s", (account)):
            cursor.execute("update users set member=\'是\' where account= \'"+str(account)+"\'");
            conn.commit()
            return "1"
        else:
            return "2"
    return "0"
#新添mxy--------------------------------------------------


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
