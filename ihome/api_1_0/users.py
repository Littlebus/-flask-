from . import api
from ihome import db
from ihome.utils.commons import login_required
from sqlalchemy.exc import IntegrityError
from ihome.utils.response_code import RET
from flask import request,jsonify,session, current_app,g
from ihome.models import User,Paper,Grade
import re




@api.route('/user', methods=['GET'])
@login_required
def get_user_profile():
    """获取用户信息
    包括：手机号，用户名,需要考试的试卷名称
    要求：json格式
    """
    # 获取用户id
    user_id = g.user_id

    # 根据用户id查询该用户的信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')
    # 判断获取的user是否为空
    # if user is None:
    #     jsonify(errno=RET.NODATA, errmsg='无效操作')

    try:
        paper = Paper.query.filter_by(state=1).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取考试信息失败')
    # 判断获取的paper是否为空
    # if paper is None:
    #     jsonify(errno=RET.NODATA, errmsg='无效操作')
    paper_dict = []
    # 将对象转化为字典
    for p in paper:
        paper_dict.append(p.to_dict())  # [{'paper_id':1,'paper_name':'卷一'}，{'paper_id':2,'paper_name':'卷二'}]

    # 返回用户的基本信息以及试卷名称
    return jsonify(errno=RET.OK, errmsg='OK', data=user.to_dict(), paper=paper_dict)


@api.route('/users/info', methods=['PUT'])
@login_required
def change_user_name():
    """修改用户个人信息，
    包括：email sex introduction
    json形式
    """
    user_id = g.user_id
    req_data = request.get_json()

    # # 判断参数的完整性
    # if req_data is None:
    #     return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 获取要修改的email sex introduction值
    email = req_data.get('email')
    sex = req_data.get('sex')
    introduction = req_data.get('introduction')

    user = User.query.filter_by(id=user_id).first()

    try:
        if sex:
            # user.sex = sex
            user.update({"sex":sex})
        if introduction:
            # user.introduction = introduction
            user.update({"introduction": introduction})
        if email:
            if not re.match(r'([\w]+(\.[\w]+)*@[\w]+(\.[\w])+)', email):
                return jsonify(errno=RET.PARAMERR, errmsg='邮箱格式错误')
            else:
                # user.email = email
                user.update({"email": email})
        # User.query.filter_by(id=user_id).update({"email": email,"sex":sex,"introduction":introduction})
        # db.session.update(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作错误后回滚
        db.session.rollback()
        # 表示手机号出现了重复，即手机号被注册过了
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg='邮箱已存在')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='修改失败')

    # 返回结果
    return jsonify(errno=RET.OK, errmsg='修改成功')


# @api.route('/user/paper', methods=['GET'])
# @login_required
# def show_paper():
#     """获取已经发布（state=1）的试卷列表
#     :return name 试卷名称
#             create_time 创建时间
#         格式 json数据
#     """
#     try:
#         papers = Paper.query.filter_by(state=1).all()
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DBERR,errmsg="获取数据失败")
#
#     # 将查询到的试卷信息以字典的形式存放在列表中
#     papers_list = []
#     for paper in papers:
#         papers_list.append(paper.to_dict())
#
#     return jsonify(errno=RET.OK,errmsg="OK", data=papers_list)

@api.route('/user/grade', methods=['POST'])
@login_required
def calGrade():
    """
    用户提交试题答案，系统完成在线判卷，只对单选题和多选题给出得分
    传入参数：
        paper_id:试卷id
        questions_id:试题id
        user_answers:用户答案（question_id与user_answer是一一对应的，比如question_id列表的第一个元素为3，即试题id为3，user_answer列表的第一个元素就是用户对id为3的试题的答案）
    :return:
    """
    user_id = g.user_id
    req_dict = request.get_json()
    paper_id = req_dict.get("paper_id")
    questions_id = req_dict.get("questions_id")
    user_answers = req_dict.get("user_answers")
    print(paper_id)
    print(questions_id)
    print(type(questions_id))
    print(user_answers)

    if not all([paper_id, questions_id,user_answers]):
        return jsonify(errno=RET.PARAMERR, errmsg='请求参数不完整')
    # 实例化对象
    try:
        user = User.query.filter_by(id=user_id).first()
        paper = Paper.query.filter_by(id=paper_id).first()
        paper_name = paper.to_dict().get("paper_name")  # 获取试卷名称
        grades = Grade.query.filter_by(user_id=user.id,paper_name=paper_name).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")
    if grades:
        return jsonify(errno=RET.DATAEXIST, errmsg="不可重复答题")
    try:
        questions = paper.questions
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")
    questions_list = []
    for question in questions:
        questions_list.append(question.to_dict())

    q_ids = []
    q_answers = []
    q_scores = []
    q_types = []
    mygrade = 0  # 初始化一个成绩为0
    for i in range(len(questions_list)):
        question_dict = questions_list[i]
        q_ids.append(question_dict.get('question_id'))  # 试卷中的试题id 列表
        q_answers.append(question_dict.get('answer'))
        q_scores.append(question_dict.get('score'))
        q_types.append(question_dict.get('type'))

    # print(q_ids)
    # print(q_answers)
    for question_id in questions_id:
        print(question_id)
        index = questions_id.index(question_id)  # 得到该题目id在列表中对应的索引值
        user_answer = user_answers[index]  # 通过索引得到用户对该题的答案
        q_index = q_ids.index(int(question_id))  # 得到题目id在试题id列表中的索引值
        ok_answer = q_answers[q_index]  # 题目对应的正确答案
        q_score = q_scores[q_index]
        if q_types[q_index] in ["单选题","多选题"]:
            if user_answer == ok_answer:
                mygrade += q_score

    grade = Grade(
        user_id=user_id,
        paper_name=paper_name,
        grade=mygrade
    )
    try:
        db.session.add(grade)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存数据异常')

    return jsonify(errno=RET.OK, errmsg="OK",grade=mygrade)





