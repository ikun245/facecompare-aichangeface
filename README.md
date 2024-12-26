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

相似度越小代表越像然后根据给出的绝对路径去搜索这个图片，应对小型离线找相似的人脸可以胜任，不用是可以暂停，使用时直接打开，有事没事还可以使用train.py想数据库里添加图片

然后是ai人脸，下载AI人脸替换工具离线版夸克链接：https://pan.quark.cn/s/35ad92b9a09a
提取码：icTu
此工具来源于b站大佬：万能君的软件库，具体使用视频在b站
