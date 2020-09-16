# -*- coding:utf-8 -*-

from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash,check_password_hash  # 生成密码，检验密码

class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


class User(BaseModel, db.Model):
    """用户"""

    __tablename__ = "ih_user_profile"

    id = db.Column(db.Integer, primary_key=True)  # 用户编号
    # username = db.Column(db.String(32), unique=True, nullable=False)  # 用户昵称
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    mobile = db.Column(db.String(11), nullable=False)  # 手机号
    name = db.Column(db.String(30),nullable=False,index=True) # 真实姓名
    email = db.Column(db.String(254),unique=True)
    sex = db.Column(db.String(32), default="男")
    introduction = db.Column(db.TEXT)
    grades = db.relationship('Grade',back_populates='user')
    # real_name = db.Column(db.String(32))  # 真实姓名
    # id_card = db.Column(db.String(20))  # 身份证号
    # avatar_url = db.Column(db.String(128))  # 用户头像路径
    # houses = db.relationship("House", backref="user")  # 用户发布的房屋
    # orders = db.relationship("Order", backref="user")  # 用户下的订单

    # 加上property装饰器后，会把函数变为属性，属性名即为函数名，但是在表中并没有password这个数据
    @property
    def password(self):
        """读取password属性时被调用"""
        raise AttributeError("不可读")

    # 使用这个装饰器，对应设置属性操作，对password进行加密操作传入到数据库中的password_hash中
    @password.setter
    def password(self, value):
        """设置密码时被调用,设置密码加密
        设置属性 user.passord = 'xxxxx'
        :param value:设置属性值时的数据，value就是xxxxx',原始的明文密码，也就是在注册时传入的密码
        :return:加密后的password_hash"""
        self.password_hash = generate_password_hash(value)

    def check_password(self,passwd):
        """
        检验密码的正确性，登陆时填写的密码与数据库中保存的加密后的密码是否一致
        :param passwd: 用户登陆时填写的密码
        :return: 如果一致，则返回true
        """
        return check_password_hash(self.password_hash,passwd)

    def to_dict(self):
        """
        将数据转换后字典
        :return: 字典
        """
        user_dict = {
            "user_id": self.id,
            "name": self.name,
            "mobile": self.mobile,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:S"),
            "email": self.email,
            "sex": self.sex,
            # "grades":self.grades,
            "introduction": self.introduction,
        }
        return user_dict


class Admin(BaseModel, db.Model):
    """管理员"""

    __tablename__ = "ih_admin_profile"

    id = db.Column(db.Integer, primary_key=True)  # 用户编号
    name = db.Column(db.String(32), nullable=False)  # 用户昵称
    password = db.Column(db.String(128), nullable=False)
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
    email = db.Column(db.String(254), unique=True)


association_table = db.Table('association_question_paper',
                             db.Column('question_id',db.Integer,db.ForeignKey('ih_question_profile.id')),
                             db.Column('paper_id',db.Integer,db.ForeignKey('ih_paper_profile.id'),primary_key=True)
                             )
class Paper(BaseModel,db.Model):
    """试卷"""

    __tablename__ = "ih_paper_profile"

    id = db.Column(db.Integer, primary_key=True)  # 试卷编号
    name = db.Column(db.String(32), nullable=False,unique=True)  # 试卷名称
    questions = db.relationship('Question',secondary=association_table,back_populates='papers')
    state = db.Column(db.Integer, default=0) # 试卷是否发布
    def to_dict(self):
        """
        将数据转换后字典
        :return: 字典
        """
        paper_dict = {
            "paper_id": self.id,
            "paper_name": self.name,
            "paper_state": self.state,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:S")
        }
        return paper_dict

class Question(BaseModel,db.Model):
    """题库"""

    __tablename__ = "ih_question_profile"

    id = db.Column(db.Integer, primary_key=True)  # 题目编号
    type = db.Column(db.String(32), nullable=False)  # 试题类型 单选/多选/简答
    title = db.Column(db.TEXT,nullable=False)
    answer = db.Column(db.TEXT,nullable=False)  # 答案
    option_A = db.Column(db.TEXT)  # A选项
    option_B = db.Column(db.TEXT)
    option_C = db.Column(db.TEXT)
    option_D = db.Column(db.TEXT)
    papers = db.relationship('Paper', secondary=association_table, back_populates='questions')
    score = db.Column(db.Integer,default=3)

    def to_dict(self):
        """
        将数据转换后字典
        :return: 字典
        """
        question_dict = {
            "question_id": self.id,
            "type": self.type,
            "title": self.title,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:S"),
            "answer": self.answer,
            "option_A": self.option_A,
            "option_B": self.option_B,
            "option_C": self.option_C,
            "option_D": self.option_D,
            "score": self.score
        }
        return question_dict


class Grade(BaseModel,db.Model):
    """成绩表"""

    __tablename__ = "ih_grade_profile"

    id = db.Column(db.Integer, primary_key=True)  # 编号
    paper_name = db.Column(db.String(32), nullable=False)  # 试卷名称
    # user_name = db.Column(db.String(32), nullable=False)
    grade = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('ih_user_profile.id'))
    user = db.relationship('User', back_populates='grades')

    def to_dict(self):
        """
        将数据转换后字典
        :return: 字典
        """
        grade_dict = {
            "grade_id": self.id,
            "paper_name": self.paper_name,
            "grade": self.grade,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:S"),
            "user_id": self.user_id,
        }
        return grade_dict


class Files(BaseModel,db.Model):
    """文件表"""

    __tablename__ = "ih_files_profile"

    id = db.Column(db.Integer, primary_key=True)  # 编号
    file_name = db.Column(db.String(200), nullable=True)  # 文件上传时的名称
    # user_name = db.Column(db.String(32), nullable=False)
    file_path = db.Column(db.String(64), nullable=True,index=True )  # 文件在服务器中保存的名称，用户根据这个名称下载文件

    def to_dict(self):
        """
        将数据转换后字典
        :return: 字典
        """
        file_dict = {
            "file_id": self.id,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:S")
        }
        return file_dict


# python app.py db migrate -m" "

# python app.py db upgrade