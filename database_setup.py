import sqlite3

# 设置SQLite数据库连接
conn = sqlite3.connect('face_database.db')
c = conn.cursor()

# 创建一个表来存储图片路径和人脸特征
c.execute('''
CREATE TABLE IF NOT EXISTS faces (
    id INTEGER PRIMARY KEY,
    image_path TEXT,
    face_encoding BLOB
)
''')
conn.commit()

# 关闭数据库连接
conn.close()
