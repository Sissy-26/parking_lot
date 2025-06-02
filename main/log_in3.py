from flask import Flask, render_template, request, redirect, url_for, flash,session,jsonify
import pymysql
import re  # 导入正则表达式模块
from datetime import datetime
from app import get_db_connection

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
            car_plate VARCHAR(20) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ✅ 创建会员表（如不存在）
def init_member():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS member (
            username VARCHAR(255) NOT NULL,
            account VARCHAR(255) NOT NULL UNIQUE,
            car_plate VARCHAR(20) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ✅ 创建并初始化车位信息表
def init_parking_slots():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_slots (
            id INT AUTO_INCREMENT PRIMARY KEY,
            number INT NOT NULL UNIQUE,
            is_reserved BOOLEAN DEFAULT FALSE,
            plate_number VARCHAR(20)
        )
    ''')
    # 检查是否已经初始化
    cursor.execute("SELECT COUNT(*) FROM parking_slots")
    count = cursor.fetchone()[0]
    if count < 55:
        for i in range(1, 56):
            cursor.execute("INSERT IGNORE INTO parking_slots (number) VALUES (%s)", (i,))
        conn.commit()
    conn.close()


# ✅ 创建黑名单表（如不存在）
def init_blacklist():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blacklist (
            time VARCHAR(255) NOT NULL,
            reason VARCHAR(255) NOT NULL ,
            car_plate VARCHAR(20) NOT NULL UNIQUE
        )
    ''')
    conn.commit()

# ✅ 创建“当日资讯”表（如不存在）
def init_daily_news():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_news (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255), 
            content TEXT NOT NULL,
            date DATE NOT NULL UNIQUE
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
def login(user_id=None):
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
            session['account'] = account #------------------------------
            session['user_id'] = user[0]  # user[0] 是 id
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
                return redirect(url_for('manage2'))
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
    username = session.get('username')
    account = session.get('account')

    # 连接 MySQL（请根据你的数据库配置替换 host/user/password/database）
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='parking_system',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            today = datetime.today().strftime('%Y-%m-%d')
            sql = "SELECT title, content, date FROM daily_news WHERE date = %s"
            cursor.execute(sql, (today,))
            news_list = cursor.fetchall()
    finally:
        connection.close()

    # 把资讯数据传给模板
    return render_template('success.html', username=username, news_list=news_list)


@app.route('/reserve_slot', methods=['GET', 'POST'])
def reserve_slot():
    if 'user_id' not in session:
        flash('请先登录才能预约车位。', 'danger')
        return redirect(url_for('login'))

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        slot_id = request.form.get('slot_id')
        user_id = session['user_id']

        # 获取当前用户车牌
        cursor.execute("SELECT car_plate FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        plate = result['car_plate'] if result else None

        # 检查该车位是否已被预约
        cursor.execute("SELECT is_reserved FROM parking_slots WHERE id = %s", (slot_id,))
        reserved = cursor.fetchone()
        if reserved and reserved['is_reserved']:
            flash('该车位已被预约，请选择其他车位。', 'danger')
        else:
            # 进行预约
            cursor.execute("""
                UPDATE parking_slots
                SET is_reserved = TRUE, plate_number = %s
                WHERE id = %s
            """, (plate, slot_id))
            conn.commit()
            flash(f'车位 {slot_id} 预约成功！', 'success')
            conn.close()
            return redirect(url_for('view_reservation'))

    # 获取所有未被预约的车位
    cursor.execute("SELECT id, number FROM parking_slots WHERE is_reserved = FALSE")
    available_slots = cursor.fetchall()
    conn.close()

    return render_template('reserve.html', slots=available_slots)

@app.route('/my_reservation')
def view_reservation():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 获取用户车牌
    cursor.execute("SELECT car_plate FROM users WHERE id = %s", (session['user_id'],))
    car = cursor.fetchone()
    if not car:
        flash('用户不存在。', 'danger')
        return redirect(url_for('reserve'))  # 修改点：返回预约页面

    car_plate = car['car_plate']

    # 查找是否有对应车位预约
    cursor.execute("""
        SELECT number FROM parking_slots
        WHERE plate_number = %s AND is_reserved = TRUE
    """, (car_plate,))
    slot = cursor.fetchone()
    conn.close()

    if not slot:
        flash('您尚未预约任何车位。', 'warning')
        return redirect(url_for('reserve_slot'))  # 修改点：返回预约页面

    return render_template('my_reservation.html', slot=slot)

@app.route('/cancel_reservation', methods=['POST'])
def cancel_reservation():
    if 'user_id' not in session:
        flash('请先登录。', 'danger')
        return redirect(url_for('login'))

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 获取用户车牌
    cursor.execute("SELECT car_plate FROM users WHERE id = %s", (session['user_id'],))
    car = cursor.fetchone()
    if not car:
        flash('用户信息获取失败。', 'danger')
        conn.close()
        return redirect(url_for('reserve_slot'))

    car_plate = car['car_plate']

    # 查找对应车位并取消预约
    cursor.execute("""
        UPDATE parking_slots
        SET is_reserved = FALSE, plate_number = NULL
        WHERE plate_number = %s AND is_reserved = TRUE
    """, (car_plate,))
    conn.commit()
    conn.close()

    flash('车位预约已取消。', 'success')
    return redirect(url_for('reserve_slot'))




@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 获取用户信息
    cursor.execute("SELECT username, account, car_plate FROM users WHERE id = %s", (session['user_id'],))
    user_info = cursor.fetchone()

    # 查询是否是会员
    cursor.execute("SELECT * FROM member WHERE account = %s", (user_info['account'],))
    member_info = cursor.fetchone()
    user_info['is_member'] = bool(member_info)  # 添加会员标志

    conn.close()

    return render_template('profile.html', user=user_info)


@app.route('/become_member', methods=['POST'])
def become_member():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 查询用户信息
    cursor.execute("SELECT username, account, car_plate FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    if user:
        # 检查是否已是会员
        cursor.execute("SELECT * FROM member WHERE account = %s", (user[1],))
        existing_member = cursor.fetchone()

        if existing_member:
            flash('您已是会员！', 'info')  # 添加闪现提示
        else:
            cursor.execute("""
                INSERT INTO member (username, account, car_plate)
                VALUES (%s, %s, %s)
            """, (user[0], user[1], user[2]))
            conn.commit()
            flash('恭喜，您已成功成为会员！', 'success')

    conn.close()
    return redirect(url_for('profile'))

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        flash('请先登录。', 'danger')
        return redirect(url_for('login'))

    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        flash('两次输入的密码不一致！', 'danger')
        return redirect(url_for('profile'))

    if not is_valid_password(new_password):
        flash('密码必须是11位以内的数字！', 'danger')
        return redirect(url_for('profile'))

    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password=%s WHERE id=%s", (new_password, session['user_id']))
        conn.commit()
        conn.close()
        flash('密码修改成功！', 'success')
    except Exception as e:
        flash('修改密码时发生错误，请重试。', 'danger')

    return redirect(url_for('profile'))


@app.route('/map')
def parking_map():
    # 示例：你可以从数据库中获取每个车位的状态
    slots = [{'number': i + 1, 'reserved': False} for i in range(55)]  # 真实项目中请从数据库加载状态
    return render_template('map.html', slots=slots)


@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/appeal')
def appeal():
    return render_template('appeal.html')


@app.route('/blacklist', methods=['GET'])
def blacklist():
    if request.method == "GET":
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("select car_plate,time,reason from blacklist")
        data = cursor.fetchall()
        temp = {}
        result = []
        if data != None:
            for i in data:
                temp['car_plate'] = i[0]
                temp['time'] = i[1]
                temp['reason'] = i[2]
                result.append(temp.copy())
            return jsonify(result)
        else:
            return jsonify([])


@app.route('/users', methods=['GET'])
def users():
    if request.method == "GET":
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "select users.account,users.car_plate,member.account from users LEFT OUTER JOIN member on ( users.account=member.account) ")
        data = cursor.fetchall()
        temp = {}
        result = []
        if data != None:
            for i in data:
                if i[0] != 'manager1' and i[0] != 'manager2':
                    temp['account'] = i[0]
                    temp['car_plate'] = i[1]
                    temp['member'] = '是' if i[2] else '否'
                    result.append(temp.copy())
            return jsonify(result)
        else:
            return jsonify([])


@app.route('/historical_records', methods=['POST'])
def historical_records():
    if request.method == "POST":
        account = request.form['account']
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("select time_entry,time_exit,car_plate,price ,state from historical_records where account=%s",
                       (account))
        data = cursor.fetchall()
        temp = {}
        result = []
        if data != None:
            for i in data:
                temp['time_entry'] = i[0]
                temp['time_exit'] = i[1]
                temp['car_plate'] = i[2]
                temp['price'] = i[3]
                temp['state'] = i[4]
                result.append(temp.copy())
            return jsonify(result)
        else:
            return jsonify([])


@app.route('/blacklist_add', methods=['POST'])
def blacklist_add():
    if request.method == "POST":
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reason = request.form['reason']
        car_plate = request.form['car_plate'].upper()  # 获取并统一转为大写
        try:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor()
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
            cursor.execute("INSERT INTO users (username, account, password, car_plate) VALUES (%s, %s, %s, %s)",
                           (username, account, password, car_plate))
            if member == "是":
                cursor.execute("INSERT INTO member (username, account, car_plate) VALUES (%s, %s, %s)",
                               (username, account, car_plate))

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

@app.route('/submit_news', methods=['POST'])
def submit_news():
    title = request.form['title']
    content = request.form['content']
    date_str = request.form['date']

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 如果存在该日期的数据，则更新；否则插入
        cursor.execute("SELECT id FROM daily_news WHERE date = %s", (date,))
        result = cursor.fetchone()

        if result:
            cursor.execute("UPDATE daily_news SET content = %s WHERE date = %s", (f"{title}：{content}", date))
        else:
            cursor.execute("INSERT INTO daily_news (content, date) VALUES (%s, %s)", (f"{title}：{content}", date))

        conn.commit()
        conn.close()
        flash('当日资讯已成功提交！')
    except Exception as e:
        print("错误：", e)
        flash('提交失败，请检查输入或稍后重试。')

    return redirect(url_for('manage2'))


@app.route('/manage2', methods=['GET', 'POST'])
def manage2():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT 
            ps.number AS slot_number,
            ps.plate_number,
            u.username,
            u.car_plate
        FROM parking_slots ps
        LEFT JOIN users u ON ps.plate_number = u.car_plate
        WHERE ps.is_reserved = TRUE
        ORDER BY ps.number
    """)
    reserved_slots = cursor.fetchall()

    conn.close()
    return render_template('manage2.html', reserved_slots=reserved_slots)




@app.route('/user_delete', methods=['GET', 'POST'])
def user_delete():
    if request.method == 'POST':
        account = request.form['account']
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        if cursor.execute("SELECT * FROM users WHERE account=%s", (account)):
            cursor.execute("delete from users  where account= \'" + str(account) + "\'");
            cursor.execute("delete from member  where account= \'" + str(account) + "\'");
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
            cursor.execute("delete from blacklist  where car_plate= \'" + str(car_plate) + "\'");
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
        cursor.execute("select username,car_plate from users where account=%s",(account))
        data=cursor.fetchone()
        if data:
            cursor.execute("INSERT INTO member (username, account, car_plate) VALUES (%s, %s, %s)",
                           (data[0], account, data[1]));
            conn.commit()
            return "1"
        else:
            return "2"
    return "0"

@app.route('/favorites')
def favorites():
    # 示例数据：用户收藏的车位信息
    favorites_list = [
        {"slot_number": "001", "timestamp": "2025-05-29 15:30"},
        {"slot_number": "007", "timestamp": "2025-05-30 09:45"},
    ]
    return render_template('favorites.html', username=session.get('username'), favorites=favorites_list)

if __name__ == '__main__':
    init_db()
    init_member()
    init_parking_slots()  # ✅ 新增：初始化车位信息表
    init_blacklist()
    init_daily_news()  # ✅ 初始化“当日资讯”表
    app.run(debug=True)



