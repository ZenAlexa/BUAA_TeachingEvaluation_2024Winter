import time
import requests
from bs4 import BeautifulSoup
from getpass import getpass
from urllib.parse import quote
from form import fill_form
import sys

session = requests.Session()

PJXT_URL = "https://spoc.buaa.edu.cn/pjxt/"
LOGIN_URL = f'https://sso.buaa.edu.cn/login?service={quote(PJXT_URL, "utf-8")}cas'

def get_token():
    try:
        response = session.get(LOGIN_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        token = soup.find('input', {'name': 'execution'})['value']
        return token
    except Exception:
        print('🔴 获取登录令牌失败，请检查网络连接或登录页面结构。')
        sys.exit(1)

def login(username, password):
    try:
        form = {
            'username': username,
            'password': password,
            'execution': get_token(),
            '_eventId': 'submit',
            'type': 'username_password',
            'submit': "LOGIN"
        }
        response = session.post(LOGIN_URL, data=form, allow_redirects=True)
        response.raise_for_status()
        if '未评价不可查看课表' in response.text:
            return True
        else:
            return False
    except Exception:
        return False

def get_latest_task():
    try:
        task_list_url = f'{PJXT_URL}personnelEvaluation/listObtainPersonnelEvaluationTasks?pageNum=1&pageSize=1'
        response = session.get(task_list_url)
        response.raise_for_status()
        task_json = response.json()
        if task_json['result']['total'] == 0:
            return None
        return (task_json['result']['list'][0]['rwid'], task_json['result']['list'][0]['rwmc'])
    except Exception:
        print('🔴 获取最新任务失败，请检查网络连接或API是否变更。')
        sys.exit(1)

def get_questionnaire_list(task_id):
    try:
        list_url = f'{PJXT_URL}evaluationMethodSix/getQuestionnaireListToTask?rwid={task_id}&pageNum=1&pageSize=999'
        response = session.get(list_url)
        response.raise_for_status()
        return response.json()['result']
    except Exception:
        print('🔴 获取问卷列表失败，请检查网络连接或API是否变更。')
        return []

def set_evaluating_method(qinfo):
    try:
        if qinfo['msid'] in ['1', '2']:
            url = f'{PJXT_URL}evaluationMethodSix/reviseQuestionnairePattern'
        elif qinfo['msid'] is None:
            url = f'{PJXT_URL}evaluationMethodSix/confirmQuestionnairePattern'
        else:
            print(f"⚠️ 未知的 msid {qinfo['msid']} 对于 {qinfo['wjmc']}")
            return
        form = {
            'wjid': qinfo['wjid'],
            'msid': 1,
            'rwid': qinfo['rwid']
        }
        response = session.post(url, json=form)
        response.raise_for_status()
    except Exception:
        print(f"🔴 设置评教方式失败: {qinfo['wjmc']}")

def get_course_list(qid):
    try:
        course_list_url = f'{PJXT_URL}evaluationMethodSix/getRequiredReviewsData?sfyp=0&wjid={qid}&pageNum=1&pageSize=999'
        response = session.get(course_list_url)
        response.raise_for_status()
        course_list_json = response.json()
        return course_list_json.get('result', [])
    except Exception:
        print(f"🔴 获取课程列表失败: {qid}")
        return []

def evaluate_single_course(cinfo, method, special_teachers):
    try:
        teacher_name = cinfo.get("pjrxm", "未知老师")
        if teacher_name in special_teachers:
            current_method = 'worst_passing'
        else:
            current_method = method
        params = {
            'rwid': cinfo["rwid"],
            'wjid': cinfo["wjid"],
            'sxz': cinfo["sxz"],
            'pjrdm': cinfo["pjrdm"],
            'pjrmc': cinfo["pjrmc"],
            'bpdm': cinfo["bpdm"],
            'bpmc': cinfo["bpmc"],
            'kcdm': cinfo["kcdm"],
            'kcmc': cinfo["kcmc"],
            'rwh': cinfo["rwh"]
        }
        topic_url = f'{PJXT_URL}evaluationMethodSix/getQuestionnaireTopic?' + '&'.join([f'{k}={quote(str(v))}' for k, v in params.items()])
        response = session.get(topic_url)
        response.raise_for_status()
        topic_json = response.json()
        if not topic_json['result']:
            print(f"⚠️ 获取评教主题失败: {cinfo['kcmc']} - 老师: {teacher_name}")
            return
        evaluate_result = fill_form(topic_json['result'][0], current_method)
        submit_url = f'{PJXT_URL}evaluationMethodSix/submitSaveEvaluation'
        submit_response = session.post(submit_url, json=evaluate_result)
        submit_response.raise_for_status()
        if submit_response.json().get('msg') == '成功':
            if teacher_name in special_teachers:
                print(f"✅ 成功评教（及格分）课程: {cinfo['kcmc']} - 老师: {teacher_name}")
            else:
                print(f"✅ 成功评教课程: {cinfo['kcmc']} - 老师: {teacher_name}")
        else:
            print(f"🔴 评教失败: {cinfo['kcmc']} - 老师: {teacher_name}")
            sys.exit(1)
    except Exception:
        print(f"🔴 评教过程中出错: {cinfo['kcmc']} - 老师: {teacher_name}")
        sys.exit(1)

def auto_evaluate(method, special_teachers):
    task = get_latest_task()
    if task is None:
        print('⚠️ 当前没有可评教的任务。')
        return
    print(f"📋 开始评教任务: {task[1]}")
    q_list = get_questionnaire_list(task[0])
    if not q_list:
        print('⚠️ 未获取到任何问卷信息。')
        return
    
    # 首先评教特定教师
    if special_teachers:
        print("\n🎯 开始对特定教师进行及格评价...")
        for q in q_list:
            c_list = get_course_list(q['wjid'])
            for c in c_list:
                teacher_name = c.get("pjrxm", "未知老师")
                if teacher_name in special_teachers:
                    if c['ypjcs'] == c['xypjcs']:
                        continue
                    print(f"🔹 评教课程: {c['kcmc']} - 老师: {teacher_name} (及格评价)")
                    evaluate_single_course(c, 'worst_passing', special_teachers)
                    time.sleep(1)
    
    # 然后评教其他教师
    print("\n📈 开始对其他教师进行评教...")
    for q in q_list:
        c_list = get_course_list(q['wjid'])
        for c in c_list:
            teacher_name = c.get("pjrxm", "未知老师")
            if teacher_name in special_teachers:
                continue  # 已经评教过
            if c['ypjcs'] == c['xypjcs']:
                continue
            print(f"🔸 评教课程: {c['kcmc']} - 老师: {teacher_name} ({method_to_emoji(method)} {method_to_text(method)})")
            evaluate_single_course(c, method, special_teachers)
            time.sleep(1)
    print('\n🏁 评教任务完成！ 如果满足了你的需求，欢迎点个star⭐')

def method_to_text(method):
    return {
        'good': '最佳评价',
        'random': '随机评价',
        'worst_passing': '最差及格评价'
    }.get(method, '未知评价方法')

def method_to_emoji(method):
    return {
        'good': '🌟',
        'random': '🎲',
        'worst_passing': '⚖️'
    }.get(method, '❓')

def main():
    print("🔐 欢迎使用 BUAA 综合评教自动化系统！\n")
    username = input('请输入用户名: ')
    password = getpass('请输入密码: ')
    print('\n🔄 正在登录...')
    if login(username, password):
        print('✅ 登录成功！\n')
        print('请选择评教方法:')
        print('1. 最佳评价 🌟')
        print('2. 随机评价 🎲')
        print('3. 最差及格评价 ⚖️')
        choice = input('请输入选择的数字（默认1）: ').strip()
        if choice == '2':
            method = 'random'
        elif choice == '3':
            method = 'worst_passing'
        else:
            method = 'good'
        print(f'\n您选择的评教方法: {method_to_emoji(method)} {method_to_text(method)}\n')
        
        special_input = input('🎯 是否有特定老师需要及格评价？（y/n）: ').strip().lower()
        special_teachers = []
        if special_input == 'y':
            teachers = input('📝 请输入需要及格评价的老师姓名，多个老师用逗号分隔: ').strip()
            special_teachers = [t.strip() for t in teachers.split(',') if t.strip()]
            if special_teachers:
                print(f"🎯 特定及格评价的老师: {', '.join(special_teachers)}\n")
            else:
                print("⚠️ 未输入有效的教师姓名，继续按选定的评教方法评教所有教师。\n")
        else:
            print("✅ 无需进行特定教师的及格评价。\n")
        
        auto_evaluate(method, special_teachers)
    else:
        print('❌ 登录失败！请检查用户名和密码是否正确。')
        sys.exit(1)

if __name__ == '__main__':
    main()