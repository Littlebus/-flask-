from . import api
from flask import request,jsonify,session, current_app
from sqlalchemy.exc import IntegrityError
from ihome import db
from ihome.utils.response_code import RET
from ihome.models import User, Admin
from werkzeug.security import generate_password_hash,check_password_hash  # 生成密码，检验密码
import re


@api.route("/users",methods=["POST"])
def register():
    """用户注册
    请求的参数：手机号mobile、学生姓名name、密码password 确认密码password2
    参数格式：json
    返回：json数据
    """
    # 获取请求的json数据，返回字典
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    name = req_dict.get("name")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")

    # 校验参数
    if not all([mobile,name,password,password2]):
        return jsonify(errno=RET.PARAMERR,errmsg="请求参数不完整")
    # 判断手机号格式
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')
    # 判断两次密码是否一致
    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg='两次密码不一致')
    # 判断手机号是否注册过，将注册信息保存到数据库中
    user = User(name=name, mobile=mobile)
    user.password = password  # 密码加密
    # from sqlalchemy.exc import IntegrityError
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作错误后回滚
        db.session.rollback()
        # 表示手机号出现了重复，即手机号被注册过了
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg='手机号已注册')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询异常')

    # 将登陆状态保存到session中
    session['name'] = name
    session['mobile'] = mobile
    session['user_id'] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg='注册成功')



@api.route('/users/sessions', methods=['POST'])
def login():
    """用户登陆
    传递参数： 手机号、密码，
    格式为：json
    """
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')

    # 验证参数的完整性
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 验证手机号的格式
    if not re.match(r'1[34578]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')

    # # 判断登陆错误的次数，超过限制，则返回
    # user_ip = request.remote_addr  # 获取用户的ip地址
    # try:
    #     access_nums = redis_store.get('access_num_%s' % user_ip)
    # except Exception as e:
    #     current_app.logger.error(e)
    # else:
    #     if access_nums is not None and int(access_nums) > constants.LOGIN_ERROR_MAX_TIMES:
    #         return jsonify(errno=RET.REQERR, errmsg='登陆失败次数过多，请稍后重试')

    # 从数据库中查询用户手机号对应的对象数据
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')

    # 将用户填写的密码与数据库中的密码进行对比验证
    if user is None or not user.check_password(password):
        # try:
        #     # 如果验证失败，记录错误次数，返回信息
        #     redis_store.incr('access_num_%s' % user_ip)
        #     redis_store.expire('access_num_%s' % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        # except Exception as e:
        #     current_app.logger.error(e)
        return jsonify(erno=RET.DATAERR, errmsg='手机号或密码错误')

    # 如果验证成功，保存登陆状态至session中
    session['name'] = user.name
    session['mobile'] = user.mobile
    session['user_id'] = user.id

    return jsonify(errno=RET.OK, errmsg='登陆成功')

@api.route('/admin/sessions', methods=['POST'])
def admin_login():
    """管理员登陆
    传递参数： 手机号、密码，
    格式为：json
    """
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')

    # 验证参数的完整性
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 验证手机号的格式
    if not re.match(r'1[34578]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    try:
        admin = Admin.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')

    # 将用户填写的密码与数据库中的密码进行对比验证
    if admin is None or not admin.password:
        return jsonify(erno=RET.DATAERR, errmsg='手机号或密码错误')

    # 如果验证成功，保存登陆状态至session中
    session['name'] = admin.name
    session['mobile'] = admin.mobile
    session['user_id'] = admin.id

    return jsonify(errno=RET.OK, errmsg='登陆成功')


@api.route('/session', methods=['GET'])
def check_login():
    """检查登陆状态
    登陆成功后会跳转到主页，主页显示用户名的name值"""
    # 尝试从session中获取用户的名字
    name = session.get('name')
    # 如果session中的name存在，则表示已经登陆，否则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg='true', data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg='false')


@api.route('/session', methods=['DELETE'])
def logout():
    """退出"""
    # 清除session数据
    session.clear()
    return jsonify(errno=RET.OK, errmsg='ok')

