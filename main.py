import os
import face_recognition
import sqlite3
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import threading


class FaceCompareApp:
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))  # 添加这一行
        self.root.title("人脸对比系统")
        self.root.geometry("1280x800")

        # 初始化数据库
        self.setup_database()

        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建界面
        self.create_frames()
        self.setup_styles()

    def setup_database(self):
        """初始化数据库"""
        try:
            self.conn = sqlite3.connect('face_database.db', check_same_thread=False)
            self.c = self.conn.cursor()
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT NOT NULL,
                    face_encoding BLOB NOT NULL
                )
            ''')
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("错误", f"初始化数据库失败: {str(e)}")

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.configure('Horizontal.TProgressbar', thickness=20)

    def create_frames(self):
        """创建界面框架"""
        # 顶部信息
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(info_frame,
                  text="人脸对比系统",
                  font=('Helvetica', 16, 'bold')).pack(side=tk.LEFT)

        self.db_info = ttk.Label(info_frame, text="")
        self.db_info.pack(side=tk.RIGHT)
        self.update_db_info()

        # 内容区域
        content = ttk.Frame(self.main_frame)
        content.pack(fill=tk.BOTH, expand=True)

        # 左侧操作区
        left_frame = ttk.LabelFrame(content, text="操作区", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 按钮
        ttk.Button(left_frame,
                   text="选择图片文件夹",
                   command=self.select_folder,
                   padding=10).pack(fill=tk.X, pady=5)

        ttk.Button(left_frame,
                   text="选择对比图片",
                   command=self.select_compare_image,
                   padding=10).pack(fill=tk.X, pady=5)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(left_frame,
                                        variable=self.progress_var,
                                        maximum=100)
        self.progress.pack(fill=tk.X, pady=10)

        # 进度标签
        self.progress_label = ttk.Label(left_frame, text="0%")
        self.progress_label.pack(fill=tk.X)

        # 预览区域
        self.preview_frame = ttk.LabelFrame(left_frame, text="当前对比图片")
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 右侧结果区
        right_frame = ttk.LabelFrame(content, text="对比结果", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 结果显示区域（带滚动条）
        self.result_canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame,
                                  orient="vertical",
                                  command=self.result_canvas.yview)

        self.result_frame = ttk.Frame(self.result_canvas)
        self.result_frame.bind(
            "<Configure>",
            lambda e: self.result_canvas.configure(
                scrollregion=self.result_canvas.bbox("all"))
        )

        self.result_canvas.create_window((0, 0), window=self.result_frame, anchor="nw")
        self.result_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status = ttk.Label(self.root,
                           textvariable=self.status_var,
                           relief=tk.SUNKEN,
                           anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)

    def update_progress(self, value, text=""):
        """更新进度条"""
        self.progress_var.set(value)
        self.progress_label.config(text=f"{value:.1f}% {text}")
        self.root.update()

    def update_db_info(self):
        """更新数据库信息"""
        try:
            self.c.execute('SELECT COUNT(*) FROM faces')
            count = self.c.fetchone()[0]
            self.db_info.config(text=f"数据库：{count} 张图片")
        except:
            self.db_info.config(text="数据库：错误")

    def select_folder(self):
        """选择文件夹并处理图片"""
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        if folder_path:
            threading.Thread(target=self.process_folder,
                             args=(folder_path,),
                             daemon=True).start()

    def process_folder(self, folder_path):
        """处理文件夹中的图片"""
        self.status_var.set("正在处理...")

        try:
            image_files = []
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_files.append(os.path.join(root, file))

            total = len(image_files)
            if total == 0:
                messagebox.showinfo("提示", "未找到图片文件")
                return

            for i, image_path in enumerate(image_files):
                try:
                    self.add_image_to_database(image_path)
                    progress = (i + 1) / total * 100
                    self.update_progress(progress, f"处理中... {i + 1}/{total}")
                except Exception as e:
                    print(f"处理图片出错 {image_path}: {str(e)}")

            self.update_db_info()
            messagebox.showinfo("完成", f"处理完成！共处理 {total} 张图片")

        except Exception as e:
            messagebox.showerror("错误", f"处理过程出错: {str(e)}")

        finally:
            self.status_var.set("就绪")
            self.update_progress(0)

    def add_image_to_database(self, image_path):
        """将图片添加到数据库"""
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            encoding = encodings[0]
            encoding_blob = sqlite3.Binary(encoding.tobytes())

            self.c.execute('''
                INSERT INTO faces (image_path, face_encoding)
                VALUES (?, ?)
            ''', (image_path, encoding_blob))

            self.conn.commit()

    def select_compare_image(self):
        """选择要对比的图片"""
        file_path = filedialog.askopenfilename(
            title="选择要对比的图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.display_preview(file_path)
            threading.Thread(target=self.compare_with_database,
                             args=(file_path,),
                             daemon=True).start()

    def display_preview(self, image_path):
        """显示预览图片"""
        try:
            for widget in self.preview_frame.winfo_children():
                widget.destroy()

            image = Image.open(image_path)
            # 调整图片大小，保持比例
            max_size = (300, 300)
            ratio = min(max_size[0] / image.size[0], max_size[1] / image.size[1])
            new_size = tuple([int(x * ratio) for x in image.size])
            image = image.resize(new_size, Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(image)
            label = ttk.Label(self.preview_frame, image=photo)
            label.image = photo
            label.pack(pady=5)

            ttk.Label(self.preview_frame,
                      text=f"文件: {os.path.basename(image_path)}").pack()
        except Exception as e:
            messagebox.showerror("错误", f"无法显示预览: {str(e)}")

    def compare_with_database(self, image_path):
        """与数据库中的图片进行对比"""
        self.status_var.set("正在对比...")

        try:
            # 清空现有结果
            for widget in self.result_frame.winfo_children():
                widget.destroy()

            # 加载并编码图片
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if not encodings:
                messagebox.showwarning("警告", "未能在图片中检测到人脸")
                return

            query_encoding = encodings[0]

            # 获取数据库中的所有编码
            self.c.execute('SELECT image_path, face_encoding FROM faces')
            all_faces = self.c.fetchall()

            if not all_faces:
                messagebox.showinfo("提示", "数据库为空")
                return

            # 计算相似度
            similarities = []
            total = len(all_faces)

            for i, (db_path, db_encoding_blob) in enumerate(all_faces):
                db_encoding = np.frombuffer(db_encoding_blob, dtype=np.float64)
                # 计算欧氏距离
                distance = np.linalg.norm(query_encoding - db_encoding)

                # 改进的相似度计算
                if distance >= 0.6:
                    similarity_percent = 0  # 距离大于0.6，认为完全不相似
                else:
                    # 在0-0.6的范围内进行映射
                    # 0.6 -> 0%
                    # 0.4 -> 60%
                    # 0.2 -> 80%
                    # 0.0 -> 100%
                    if distance <= 0.2:
                        similarity_percent = 80 + (0.2 - distance) / 0.2 * 20
                    elif distance <= 0.4:
                        similarity_percent = 60 + (0.4 - distance) / 0.2 * 20
                    else:  # 0.4 < distance < 0.6
                        similarity_percent = (0.6 - distance) / 0.2 * 60

                similarities.append((db_path, similarity_percent))
                progress = (i + 1) / total * 100
                self.update_progress(progress, f"对比中... {i + 1}/{total}")

            # 按相似度降序排序（百分比越高越相似）
            similarities.sort(key=lambda x: x[1], reverse=True)

            ttk.Label(self.result_frame,
                      text="对比结果（相似度标准：80%以上极可能是同一人，60-80%很可能是同一人）",
                      font=('Helvetica', 12, 'bold')).pack(pady=10)

            # 显示前10个最相似的结果
            for i, (img_path, similarity) in enumerate(similarities[:50], 1):
                self.create_result_item(i, img_path, similarity)

        except Exception as e:
            messagebox.showerror("错误", f"对比过程出错: {str(e)}")

        finally:
            self.status_var.set("就绪")
            self.update_progress(0)

    def create_result_item(self, index, image_path, similarity):
        """创建结果项"""
        try:
            item_frame = ttk.Frame(self.result_frame)
            item_frame.pack(fill=tk.X, pady=5, padx=5)

            # 加载图片
            image = Image.open(image_path)
            image.thumbnail((150, 150))
            photo = ImageTk.PhotoImage(image)

            # 图片标签
            img_label = ttk.Label(item_frame, image=photo)
            img_label.image = photo
            img_label.pack(side=tk.LEFT, padx=5)

            # 信息区域
            info_frame = ttk.Frame(item_frame)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # 根据相似度设置不同的显示样式
            similarity_text = f"#{index} 相似度: {similarity:.1f}%"
            if similarity >= 80:
                similarity_text += " (极可能是同一个人)"
                fg_color = '#2E7D32'  # 深绿色
            elif similarity >= 60:
                similarity_text += " (很可能是同一个人)"
                fg_color = '#1976D2'  # 蓝色
            elif similarity >= 40:
                similarity_text += " (可能是同一个人)"
                fg_color = '#FB8C00'  # 橙色
            else:
                similarity_text += " (可能不是同一个人)"
                fg_color = '#757575'  # 灰色

            ttk.Label(info_frame,
                      text=similarity_text,
                      font=('Helvetica', 10, 'bold')).pack(anchor='w')

            ttk.Label(info_frame,
                      text=f"文件: {os.path.basename(image_path)}",
                      wraplength=300).pack(anchor='w')

            # 打开文件夹按钮
            ttk.Button(info_frame,
                       text="打开所在文件夹",
                       command=lambda: self.open_file_location(image_path)).pack(anchor='w', pady=5)

            # 分隔线
            ttk.Separator(self.result_frame, orient='horizontal').pack(fill=tk.X, pady=5)

        except Exception as e:
            print(f"创建结果项出错: {str(e)}")
    def open_file_location(self, file_path):
        """打开文件所在文件夹"""
        try:
            folder_path = os.path.dirname(file_path)
            os.startfile(folder_path) if os.name == 'nt' else os.system(f'xdg-open "{folder_path}"')
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")


def main():
    root = tk.Tk()
    app = FaceCompareApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
    try:
        root = tk.Tk()
        app = FaceCompareApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("错误", str(e))
        # 保持窗口显示，不立即退出
        input("按回车键退出...")