from . import api
from ihome import db
from ihome.utils.commons import login_required
from flask import request,jsonify,session, current_app,g,send_from_directory
from ihome.utils.response_code import RET
from sqlalchemy.exc import IntegrityError
from ihome.models import Question,User,Paper,Files
from random import sample
import os
import time
from werkzeug.utils import secure_filename
import base64


# POST http://127.0.0.1:5000/api/v1.0/admin/question
@api.route('/admin/question',methods=['POST'])
@login_required
def question():
    """添加试题功能
    传递参数：type：单选题，多选题，简答题
              answer
              title：题目标题
              option_A/option_B/option_C/option_D：若题目类型是选择题，需要传递选项值
    格式要求：json
    :return 若传入参数不完整，{"errno":"4103","errmsg":"请求参数不完整"}
    """
    # 获取请求的json数据，返回字典
    req_dict = request.get_json()
    q_type = req_dict.get('type')
    q_answer = req_dict.get('answer')
    q_title = req_dict.get('title')
    q_option_A = req_dict.get('option_A')
    q_option_B = req_dict.get('option_B')
    q_option_C = req_dict.get('option_C')
    q_option_D = req_dict.get('option_D')
    q_score = req_dict.get('score')

    if not all([q_type,q_title,q_answer]):
        return jsonify(errno=RET.PARAMERR,errmsg="请求参数不完整")

    # if q_type == "单选题"or"多选题":
    if q_type in ["单选题","多选题"]:
        if not all([q_option_A, q_option_B, q_option_C, q_option_D]):
            return jsonify(errno=RET.PARAMERR, errmsg="选项参数不完整")

    question = Question(type=q_type, answer=q_answer, title=q_title, option_A=q_option_A, option_B=q_option_B, option_C=q_option_C, option_D=q_option_D,score=q_score)

    try:
        db.session.add(question)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询异常')

    return jsonify(errno=RET.OK, errmsg='添加成功',data=question.id)


# GET http://127.0.0.1:5000/api/v1.0/admin/question
@api.route('/admin/question', methods=['GET'])
@login_required
def search_question():
    """查询题库功能"""
    try:
        questions = Question.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取信息失败')

    # # 判断获取的user是否为空
    # if questions is None:
    #     jsonify(errno=RET.NODATA, errmsg='无效操作')

    questions_dict = []
    for question in questions:
        questions_dict.append(question.to_dict())
    print(questions_dict)
    return jsonify(errno=RET.OK, errmsg='OK', data=questions_dict)

# PUT http://127.0.0.1:5000/api/v1.0/admin/question
@api.route('/admin/question', methods=['PUT'])
@login_required
def update_question():
    """修改题库中的试题
    传递参数 question_id 试题id
            type：单选题，多选题，简答题
            answer
            title：题目标题
            option_A/option_B/option_C/option_D：若题目类型是选择题，需要传递选项值
            """
    req_dict = request.get_json()
    if req_dict is None:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    q_id = req_dict.get("question_id")
    q_answer = req_dict.get('answer')
    q_title = req_dict.get('title')
    q_option_A = req_dict.get('option_A')
    q_option_B = req_dict.get('option_B')
    q_option_C = req_dict.get('option_C')
    q_option_D = req_dict.get('option_D')
    q_score = req_dict.get('score')
    try:
        question = Question.query.get(q_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")

    if question.type in ["单选题","多选题"]:
        try:
            if q_answer:
                question.answer = q_answer
                # question.update({"answer":q_answer})
            if q_title:
                question.title=q_title
                # question.update({"title": q_title})
            if q_option_A:
                question.option_A=q_option_A
                # question.update({"option_A": q_option_A})
            if q_option_B:
                question.option_B=q_option_B
                # question.update({"option_B": q_option_B})
            if q_option_C:
                question.option_C=q_option_C
                # question.update({"option_A": q_option_C})
            if q_option_D:
                question.option_D=q_option_D
                # question.update({"option_A": q_option_D})
            if q_score:
                question.score=q_score

            db.session.add(question)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='修改失败')
    else:
        try:
            if q_answer:
                question.answer = q_answer
                # question.update({"answer":q_answer})
            if q_title:
                question.title = q_title
                # question.update({"title": q_title})
            if q_score:
                question.score=q_score
            db.session.add(question)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='修改失败')

    return jsonify(errno=RET.OK, errmsg='修改成功')


# DELETE http://127.0.0.1:5000/api/v1.0/admin/question
@api.route('/admin/question', methods=['DELETE'])
@login_required
def delete_question():
    """删除题库中的试题
    传递参数 question_id 试题id
            """
    req_dict = request.get_json()
    if req_dict is None:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    q_id = req_dict.get("question_id")
    try:
        question = Question.query.get(q_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")
    try:
        db.session.delete(question)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='删除失败')

    return jsonify(errno=RET.OK, errmsg='删除成功')


@api.route('/admin/search', methods=['POST'])
@login_required
def search():
    """按姓名查找用户信息功能
    传递参数：name 需要查询的用户名字
    格式要求：json

    """
    # 获取请求的json数据，返回字典
    req_dict = request.get_json()
    u_name = req_dict.get('name')
    if req_dict is None:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    try:
        users = User.query.filter_by(name=u_name).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')

    # # 判断获取的user是否为空
    # if users is None:
    #     jsonify(errno=RET.NODATA, errmsg='无效操作')

    users_dict = []
    grade_dict=[]
    for user in users:
        users_dict.append(user.to_dict())
        user_grades = user.grades
        for usr_grade in user_grades:
            grade_dict.append(usr_grade.to_dict())
    return jsonify(errno=RET.OK, errmsg='OK', data=users_dict,grade=grade_dict)

@api.route('/admin/user', methods=['GET'])
@login_required
def user():
    """用户管理功能
    传递参数：name 需要查询的用户名字
    格式要求：json

    """
    # 获取请求的json数据，返回字典
    req_dict = request.get_json()
    try:
        users = User.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')

    # # 判断获取的user是否为空
    # if users is None:
    #     jsonify(errno=RET.NODATA, errmsg='无效操作')

    users_dict = []
    grade_dict = []
    for user in users:
        users_dict.append(user.to_dict())
        user_grades = user.grades
        for usr_grade in user_grades:
            grade_dict.append(usr_grade.to_dict())
    return jsonify(errno=RET.OK, errmsg='OK', data=users_dict, grade=grade_dict)


@api.route('/admin/paper', methods=['POST'])
@login_required
def add_paper():
    """添加试卷:通过传递过来的数据从题库中随机抽取试题
    传递参数：
        name 要添加的试卷名称
        type_single 要添加的单选题
        single_num  单选题数量
        type_multiple 多选题
        multiple_num 多选题数量
        type_discussion 简答题
        discussion_num 简答题数量
    格式要求：json
    """
    req_dict = request.get_json()
    name = req_dict.get('name')
    type_single = req_dict.get('type_single')
    single_num = int(req_dict.get('single_num'))
    # single_scole = int(req_dict.get('single_scole'))
    type_multiple = req_dict.get('type_multiple')
    multiple_num = int(req_dict.get('multiple_num'))
    # multiple_scole = int(req_dict.get('multiple_scole'))
    type_discussion = req_dict.get('type_discussion')
    discussion_num = int(req_dict.get('discussion_num'))
    # discussion_scole = int(req_dict.get('discussion_scole'))

    if not all([name, type_single,single_num,type_multiple,multiple_num,type_discussion,discussion_num]):
        return jsonify(errno=RET.PARAMERR, errmsg='请求参数不完整')

    # 过滤前端传来的试题类型，防止传来的试题类型数据库中不存在
    try:
        questions = Question.query.filter(Question.type.in_([type_single,type_multiple,type_discussion])).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询异常')

    paper = Paper(name=name)

    if questions:
        # 有合法的试题类型
        # type_questions_dict = []
        # type_questions_id = []
        paper_questions_id = []
        # question_type = ['单选题','多选题','简答题']
        # question_num = [single_num,multiple_num,multiple_num]
        type_dict = {type_single:single_num,type_multiple:multiple_num,type_discussion:discussion_num}
        # type_dict= {'单选题':single_num,'多选题':multiple_num,'简答题':discussion_num}
        for question_type, num in type_dict.items():
            type_questions_dict = []
            type_questions_id = []
            # 返回题库中所有question_type类型的对象
            type_questions = Question.query.filter_by(type=question_type).all()
            for type_question in type_questions:
                type_questions_dict.append(type_question.to_dict())
            # print("--------------------------------------------------------------------------------------")
            # print(type_questions_dict)
            # print(type_questions_id)
            # 获取相关类型问题的id列表
            for i in range(len(type_questions_dict)):
                question_id_dict = type_questions_dict[i]
                type_questions_id.append(question_id_dict.get('question_id'))
            print("----------------------------------------------------------------------------")
            print(type_questions_id)

            # 从question_type类型的问题id中随机抽取question_type_num个元素
            paper_type_question_id = sample(type_questions_id, num) # [13, 19, 12, 9, 3]
            # print("------------------------------------------------------------------------------")
            # print(paper_type_question_id)
            for id in paper_type_question_id:
                paper_questions_id.append(id)
            # print("---------------------------------------------------------------------------------")
            # print(paper_questions_id)
            # paper_questions_id.append(paper_type_question_id)
            # 查询随机抽取的题目id对应的对象
        try:
            paper_questions = Question.query.filter(Question.id.in_(paper_questions_id)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库查询异常')
        paper.questions = paper_questions
        try:
            db.session.add(paper)
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后回滚
            db.session.rollback()
            # 表示试卷名称出现了重复
            current_app.logger.error(e)
            return jsonify(errno=RET.DATAEXIST, errmsg='试卷已存在')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='保存数据异常')

        return jsonify(errno=RET.OK, errmsg="OK", data=paper.id)


@api.route('/admin/paper', methods=['GET'])
@login_required
def search_paper():
    """查询试卷列表
    :return name 试卷名称
            create_time 创建时间
        格式 json数据
    """
    try:
        papers = Paper.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取数据失败")

    # 将查询到的试卷信息以字典的形式存放在列表中
    papers_list = []
    for paper in papers:
        papers_list.append(paper.to_dict())

    return jsonify(errno=RET.OK,errmsg="OK", data=papers_list)


@api.route('/admin/paper', methods=['PUT'])
@login_required
def update_paper():
    """修改试卷：可以修改试卷的名称以及修改的发布状态，0表示未发布，1表示发布
        传入参数：试卷id
        格式 json数据
    """
    req_dict = request.get_json()
    if req_dict is None:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    paper_id = req_dict.get('paper_id')
    paper_state = req_dict.get('paper_state')
    paper_name = req_dict.get('paper_name')
    try:
        paper = Paper.query.get(paper_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")
    try:
        if paper_name:
            paper.name = paper_name
        if paper_state:
            paper.state = paper_state
        db.session.add(paper)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='修改失败')

    return jsonify(errno=RET.OK,errmsg="修改成功")


@api.route('/admin/paper', methods=['DELETE'])
@login_required
def delete_paper():
    """删除试卷
        传入参数：试卷id
        格式 json数据
    """
    req_dict = request.get_json()
    if req_dict is None:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    paper_id = req_dict.get('paper_id')
    try:
        paper = Paper.query.get(paper_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")
    try:
        db.session.delete(paper)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='删除失败')

    return jsonify(errno=RET.OK, errmsg='删除成功')


@api.route('/paper/question', methods=['POST'])
@login_required
def show_paper_question():
    """查询某一试卷中的试题
        传入参数：试卷id
        格式 json数据
    """
    req_dict = request.get_json()
    if req_dict is None:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    paper_id = req_dict.get('paper_id')
    try:
        paper = Paper.query.get(paper_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")

    try:
        questions = paper.questions
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")

    questions_dict = []
    for question in questions:
        questions_dict.append(question.to_dict())
    return jsonify(errno=RET.OK, errmsg='OK', data=questions_dict)



# 用于判断文件后缀
def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF','docx','pdf'])
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 上传文件
@api.route('/file/upload', methods=['POST'], strict_slashes=False)
@login_required
def api_upload():
    """"上传文件"""
    file_dir = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值

    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        # fname = secure_filename(f.filename)
        fname  = f.filename
        print(fname)
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        new_filename = str(unix_time) + '.' + ext  # 修改了上传的文件名
        print(new_filename)
        f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录

        try:
            file = Files(file_name=fname,file_path=new_filename)
            db.session.add(file)
            db.session.commit()
            return jsonify(errno=RET.OK, errmsg='OK')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='保存数据库失败')

    else:
        return jsonify(errno=RET.DATAERR, errmsg="上传失败")

@api.route('/file/upload', methods=['GET'], strict_slashes=False)
@login_required
def show_files():
    """获取文件"""
    try:
        files = Files.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取数据失败")

    # 将查询到的试卷信息以字典的形式存放在列表中
    files_list = []
    for file in files:
        files_list.append(file.to_dict())

    return jsonify(errno=RET.OK,errmsg="OK", data=files_list)

@api.route('/file/download', methods=['POST'], strict_slashes=False)
@login_required
def down_file():
    """下载文件
    传入参数：file_name：在服务器存储的真实文件名，也就是数据库中的file_path"""
    req_dict = request.get_json()
    if req_dict is None:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    file_name = req_dict.get('file_name')
    file_dir = current_app.config['UPLOAD_FOLDER']
    try:
        if os.path.isfile(os.path.join(file_dir,file_name)):
            return send_from_directory(file_dir,file_name,as_attachment=True)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="文件下载失败")



