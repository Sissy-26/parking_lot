import pymysql

# 连接 MySQL（不连接到特定数据库）
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='root',  # 请替换成你的 MySQL 密码
    charset='utf8'  # 确保使用 utf8 字符集
)

cursor = conn.cursor()

# 创建数据库（如果不存在）
try:
    cursor.execute("CREATE DATABASE IF NOT EXISTS parking_system DEFAULT CHARACTER SET utf8")
    print("✅ 数据库 'parking_system' 创建成功或已存在。")
except Exception as e:
    print("❌ 创建数据库失败：", e)

# 关闭连接
cursor.close()
conn.close()
