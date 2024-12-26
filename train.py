import os
import face_recognition
import sqlite3
import numpy as np

# 设置数据库连接
conn = sqlite3.connect('face_database.db', check_same_thread=False)
c = conn.cursor()


# 提取图片并存储人脸特征
def add_image_to_database(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)

    if encodings:  # 如果找到了人脸
        encoding = encodings[0]  # 取第一张人脸的编码
        encoding_blob = sqlite3.Binary(encoding.tobytes())  # 将编码转换为BLOB存储
        c.execute('''
        INSERT INTO faces (image_path, face_encoding) VALUES (?, ?)
        ''', (image_path, encoding_blob))
        conn.commit()
        print(f"Image {image_path} added to database successfully.")
    else:
        print(f"No face detected in image {image_path}")


# 获取目录下的所有图片并添加到数据库
def add_images_from_directory(directory_path):
    # 获取目录下所有的图片文件
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path) and file_path.lower().endswith(('png', 'jpg', 'jpeg')):
            add_image_to_database(file_path)


# 调用方法，指定你的图片目录
directory_path = r'C:\Users\12271\Downloads\Telegram Desktop\3'  # 替换为你的图片文件夹路径
add_images_from_directory(directory_path)
print("Finished adding images to database.")
