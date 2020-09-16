# -*- coding: utf-8 -*-
import redis





class Config(object):
    """配置信息"""
    SECRET_KEY = "dhsodfhisfhosdhf29fy989"

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:timeinan11@127.0.0.1:3306/db_medical_test"
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # # 设置sqlalchemy自动跟踪数据库

    # redix
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # flask-session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port = REDIS_PORT)
    SESSION_USE_SIGNER = True  # 对cookie中的session_id进行隐藏
    PERMANENT_SESSION_LIFETIME = 86400  # session数据的有效期，单位秒











class DevelopmentConfig(Config):
    """开发模式配置信息"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置信息"""
    pass

config_map ={
    'develop':DevelopmentConfig,
    'product':ProductionConfig
}