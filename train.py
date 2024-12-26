import os
import face_recognition
import sqlite3
import numpy as np

conn = sqlite3.connect('face_database.db', check_same_thread=False)
c = conn.cursor()


def add_image_to_database(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)

    if encodings:  
        encoding = encodings[0]  
        encoding_blob = sqlite3.Binary(encoding.tobytes()) 
        c.execute('''
        INSERT INTO faces (image_path, face_encoding) VALUES (?, ?)
        ''', (image_path, encoding_blob))
        conn.commit()
        print(f"Image {image_path} added to database successfully.")
    else:
        print(f"No face detected in image {image_path}")


def add_images_from_directory(directory_path):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path) and file_path.lower().endswith(('png', 'jpg', 'jpeg')):
            add_image_to_database(file_path)


directory_path = r'绝对路径'  # 替换为你的图片文件夹路径
add_images_from_directory(directory_path)
print("Finished adding images to database.")
