from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
import functools
from ihome.utils.response_code import RET


class ReConverter(BaseConverter):
    """定义正则转换器"""
    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        # 将正则表达式的参数保存到对象的属性中，flask会去使用这个属性来进行路由的正则匹配
        self.regex = regex


# 定义检验登陆状态的装饰器
def login_required(view_func):
    # @functools.wraps(view_func)时为了保证不改变被装饰函数的属性值
    # 不加@functools.wraps(view_func)时被装饰函数的__name__属性值变成了wrapper
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户的登陆状态
        user_id = session.get('user_id')

        # 如果用户是登陆的，执行视图函数
        if user_id is not None:
            # g:处理请求时，用于临时存储的对象，每次请求都会重设这个变量。
            # 比如：我们可以获取一些临时请求的用户信息。
            # 在被装饰的函数中可以直接调用 user_id = g.user_id
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 未登录，返回未登录的信息
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    return wrapper
