# -*- coding: utf-8 -*-
import logging
from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_session import Session
from flask_wtf import CSRFProtect
from logging.handlers import RotatingFileHandler
from ihome.utils.commons import ReConverter
import os


# 创建数据库sqlalchemy工具对象
db = SQLAlchemy()

# # 创建redix连接对象
# redis_store = None
#
# 为flask补充防护机制
csrf = CSRFProtect()

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调式debug等级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler('logs/log',maxBytes=1024*1024*100,backupCount=10)
# 创建日志记录的格式
formatter = logging.Formatter("%(levelname)s - %(filename)s:%(lineno)d  %(message)s")
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的） 添加日志记录器
logging.getLogger().addHandler(file_log_handler)


# 工厂模式
def create_app(config_name):
    """
    创建flask的应用对象
    :param:str 配置模式的名字（'develop','product'）
    :return:
    """
    app = Flask(__name__)

    # 根据配置模式的名字获取配置参数的类
    config_clss = config_map.get(config_name)
    app.config.from_object(config_clss)

    # 使用app初始化db
    db.init_app(app)

    # 文件下载路径
    pwd = os.path.dirname(__file__)
    UPLOAD_FOLDER = os.path.join(pwd,'save_file')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # # 初始化redis工具
    # global redis_store
    # redis_store = redis.StrictRedis(host=config_clss.REDIS_HOST, port=config_clss.REDIS_PORT)

    # # 利用flask-session将session数据保存到redis中
    # Session(app)

    # # 为flask补充csrf防护
    # CSRFProtect(app)

    # 为flask添加自定义的转化器
    app.url_map.converters["re"] = ReConverter  # 调用转换器的时候直接使用re()

    # 注册蓝图
    from ihome import api_1_0  # 注册蓝图时在导入 防止循环导入
    app.register_blueprint(api_1_0.api, url_prefix='/api/v1.0')

    return app
