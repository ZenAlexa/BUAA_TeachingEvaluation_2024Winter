"""
CLI entry point for BUAA evaluation
For GUI mode, use: python -m backend.main
"""

import time
import sys
from getpass import getpass
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from backend.evaluator import fill_form

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
        print('[!] 获取登录令牌失败，检查网络或页面结构是否变化')
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
        print('[!] 获取任务失败，检查网络或接口是否变更')
        sys.exit(1)

def get_questionnaire_list(task_id):
    try:
        list_url = f'{PJXT_URL}evaluationMethodSix/getQuestionnaireListToTask?rwid={task_id}&pageNum=1&pageSize=999'
        response = session.get(list_url)
        response.raise_for_status()
        return response.json()['result']
    except Exception:
        print('[!] 获取问卷列表失败')
        return []

def set_evaluating_method(qinfo):
    try:
        if qinfo['msid'] in ['1', '2']:
            url = f'{PJXT_URL}evaluationMethodSix/reviseQuestionnairePattern'
        elif qinfo['msid'] is None:
            url = f'{PJXT_URL}evaluationMethodSix/confirmQuestionnairePattern'
        else:
            print(f"[?] 未知 msid: {qinfo['msid']} ({qinfo['wjmc']})")
            return
        form = {
            'wjid': qinfo['wjid'],
            'msid': 1,
            'rwid': qinfo['rwid']
        }
        response = session.post(url, json=form)
        response.raise_for_status()
    except Exception:
        print(f"[!] 设置评教方式失败: {qinfo['wjmc']}")

def get_course_list(qid):
    try:
        course_list_url = f'{PJXT_URL}evaluationMethodSix/getRequiredReviewsData?sfyp=0&wjid={qid}&pageNum=1&pageSize=999'
        response = session.get(course_list_url)
        response.raise_for_status()
        course_list_json = response.json()
        return course_list_json.get('result', [])
    except Exception:
        print(f"[!] 获取课程列表失败: {qid}")
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
            print(f"[?] 获取评教题目失败: {cinfo['kcmc']} - {teacher_name}")
            return
        evaluate_result = fill_form(topic_json['result'][0], current_method)
        submit_url = f'{PJXT_URL}evaluationMethodSix/submitSaveEvaluation'
        submit_response = session.post(submit_url, json=evaluate_result)
        submit_response.raise_for_status()
        if submit_response.json().get('msg') == '成功':
            mark = "(及格)" if teacher_name in special_teachers else ""
            print(f"[ok] {cinfo['kcmc']} - {teacher_name} {mark}")
        else:
            print(f"[!] 评教失败: {cinfo['kcmc']} - {teacher_name}")
            sys.exit(1)
    except Exception:
        print(f"[!] 评教出错: {cinfo['kcmc']} - {teacher_name}")
        sys.exit(1)

def auto_evaluate(method, special_teachers):
    task = get_latest_task()
    if task is None:
        print('当前没有评教任务')
        return
    print(f"\n任务: {task[1]}\n")
    q_list = get_questionnaire_list(task[0])
    if not q_list:
        print('未找到问卷')
        return

    if special_teachers:
        print("-- 指定教师(及格) --")
        for q in q_list:
            c_list = get_course_list(q['wjid'])
            for c in c_list:
                teacher_name = c.get("pjrxm", "未知")
                if teacher_name in special_teachers:
                    if c['ypjcs'] == c['xypjcs']:
                        continue
                    evaluate_single_course(c, 'worst_passing', special_teachers)
                    time.sleep(1)

    print("-- 其他教师 --")
    for q in q_list:
        c_list = get_course_list(q['wjid'])
        for c in c_list:
            teacher_name = c.get("pjrxm", "未知")
            if teacher_name in special_teachers:
                continue
            if c['ypjcs'] == c['xypjcs']:
                continue
            evaluate_single_course(c, method, special_teachers)
            time.sleep(1)
    print('\n完成! 好用的话给个 star :)')

def method_to_text(method):
    return {
        'good': '全好评',
        'random': '随机',
        'worst_passing': '及格线'
    }.get(method, '?')

def main():
    print("BUAA 评教助手\n")
    username = input('用户名: ')
    password = getpass('密码: ')
    print('\n登录中...')
    if login(username, password):
        print('登录成功\n')
        print('评教方式:')
        print('  1. 全好评 (默认)')
        print('  2. 随机')
        print('  3. 及格线')
        choice = input('选择 [1]: ').strip()
        if choice == '2':
            method = 'random'
        elif choice == '3':
            method = 'worst_passing'
        else:
            method = 'good'
        print(f'-> {method_to_text(method)}')

        special_input = input('\n有要单独打及格的老师? (y/n) [n]: ').strip().lower()
        special_teachers = []
        if special_input == 'y':
            teachers = input('老师姓名 (逗号分隔): ').strip()
            special_teachers = [t.strip() for t in teachers.split(',') if t.strip()]
            if special_teachers:
                print(f"-> 及格: {', '.join(special_teachers)}")

        auto_evaluate(method, special_teachers)
    else:
        print('[!] 登录失败，检查账号密码')
        sys.exit(1)

if __name__ == '__main__':
    main()