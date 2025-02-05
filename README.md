由python编写，本地离线可以运行直接使用的小型人脸对比识别，使用了第三方库Face_recognition

软件部分地方参考了chatgpt4.0的建议，如有不足欢迎探讨
		
这是一个基于 Python 的人脸识别库，使用了深度学习模型来检测和比较人脸。你可以通过它提取每张人脸的特征向量，并计算特征向量之间的相似度。

GitHub 链接：https://github.com/ageitgey/face_recognition

使用工具为Pycharm
cmd安装第三方库（我的解释器用的自带的python3.12）
具体需要的库放在requirement.txt


相似度越小代表越像然后根据给出的绝对路径去搜索这个图片，应对小型离线找相似的人脸可以胜任，不用是可以暂停，使用时直接打开，有事没事还可以使用train.py想数据库里添加图片

