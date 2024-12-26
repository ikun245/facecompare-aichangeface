由python编写，本地离线可以运行直接使用的小型人脸对比识别，使用了第三方库Face_recognition

这是一个基于 Python 的人脸识别库，使用了深度学习模型来检测和比较人脸。你可以通过它提取每张人脸的特征向量，并计算特征向量之间的相似度。

GitHub 链接：https://github.com/ageitgey/face_recognition

使用工具为Pycharm
cmd安装第三方库（我的解释器用的自带的python3.12）
具体需要的库放在requirement.txt

运行一下database_setup.py,生成一个数据库（.db）结尾名字为face_database.db用于存储图片的数据

然后运行train.py将带有人脸的图片（修改最下面的绝对路径到文件夹文件注释已标注），将数据传输到数据库

然后使用app.py,由Flask Web应用，生成本地地址，用chrome或者其他浏览器打开地址

为了美观，添加了一个templates/index.html，如果不喜欢可以修改

还有一个文件夹/uploads用于存储本地web上传的人脸图片

具体项目文件夹格式

/app.py

/templates/index.html

/uploads

/train.py

/database_setup.py

/face_database.db
