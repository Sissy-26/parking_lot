import pymysql
import datetime 
import math

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': "123456",
    'database': 'parking_system',
    'charset': 'utf8'
}

while 1:
    car_plate=input('请输入车辆出入信息（车牌号）：')
    state=input('请输入车辆状态（en/ex）：')       
    #进入停车场
    if state=='en':
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT account FROM users WHERE car_plate=%s", (car_plate))
        user = cursor.fetchone()
        account=user[0]
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO historical_records (time_entry, time_exit, account,car_plate,state) VALUES (%s,NULL, %s,%s,0)",
                       (time, account,car_plate))
        conn.commit()
    #离开停车场
    else:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        time_ex=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp_ex=datetime.datetime.strptime(time_ex, "%Y-%m-%d %H:%M:%S").timestamp()
        cursor.execute("SELECT time_entry FROM historical_records WHERE car_plate=%s and state=0 and time_exit is NULL", (car_plate))
        record=cursor.fetchone()
        time_en=record[0]
        timestamp_en=datetime.datetime.strptime(time_en, "%Y-%m-%d %H:%M:%S").timestamp()
        price=math.ceil((timestamp_ex-timestamp_en)/3600)*5
        cursor.execute("update historical_records set time_exit=%s,price=%s where car_plate=%s and state=0 and time_exit is NULL",(time_ex,price,car_plate));
        conn.commit()
    conn.close()
