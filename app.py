import os
import face_recognition
import sqlite3
import numpy as np
from flask import Flask, request, jsonify, send_from_directory, render_template

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # 图片上传的文件夹
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # 允许上传的文件类型

# SQLite 数据库连接
conn = sqlite3.connect('face_database.db', check_same_thread=False)
c = conn.cursor()

# 创建数据库表（如果尚未存在）
c.execute('''
CREATE TABLE IF NOT EXISTS faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT NOT NULL,
    face_encoding BLOB NOT NULL
)
''')
conn.commit()

# 提取图片并存储人脸特征
def add_image_to_database(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if encodings:  # 如果找到了人脸
        encoding = encodings[0]
        encoding_blob = sqlite3.Binary(encoding.tobytes())
        c.execute('''
        INSERT INTO faces (image_path, face_encoding) VALUES (?, ?)
        ''', (image_path, encoding_blob))
        conn.commit()

# 获取所有人脸特征
def get_all_encodings():
    c.execute('SELECT id, image_path, face_encoding FROM faces')
    faces = c.fetchall()
    all_encodings = []
    for face in faces:
        encoding = np.frombuffer(face[2], dtype=np.float64)
        all_encodings.append((face[1], encoding))
    return all_encodings

# 计算两个编码之间的相似度
def compare_faces(encoding1, encoding2):
    return np.linalg.norm(encoding1 - encoding2)

# 查找相似的人脸
def find_similar_faces(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        return []

    query_encoding = encodings[0]
    all_encodings = get_all_encodings()

    similarities = []
    for db_image_path, db_encoding in all_encodings:
        similarity = compare_faces(query_encoding, db_encoding)
        similarities.append((db_image_path, similarity))

    similarities.sort(key=lambda x: x[1])
    return similarities[:10]  # 返回最相似的前10张图片

# 允许上传图片的接口
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # 查找相似图片
    result = find_similar_faces(file_path)

    similar_faces = []
    for img_path, sim in result:
        similar_faces.append({'image_path': img_path, 'similarity': round(sim, 2)})

    return jsonify({'similar_faces': similar_faces})

# 首页路由，显示上传图片的页面
@app.route('/')
def index():
    return render_template('index.html')

# 提供上传的图片
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
