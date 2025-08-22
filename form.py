import random
from dataclasses import dataclass

@dataclass
class Option:
    id: str
    content: str
    pts: float

@dataclass
class Question:
    isChoice: bool
    type: str
    id: str
    options: list

def fill_form(form_info, method='good'):
    basic_info = form_info['pjxtPjjgPjjgckb'][1]
    question_list = get_question_list(form_info)
    choice_list = [q for q in question_list if q.isChoice]
    other_list = [q for q in question_list if not q.isChoice]
    if method == 'good':
        choice_answer = gen_good_answer(choice_list)
    elif method == 'random':
        choice_answer = gen_random_answer(choice_list)
    elif method == 'worst_passing':
        choice_answer = gen_worst_passing_answer(choice_list)
    else:
        raise ValueError(f"未知的方法 {method}")
    enforce_rules(choice_answer, choice_list)
    total_score = int(sum(q.pts for q in choice_answer if q))
    answer_list = []
    for i in range(len(choice_list)):
        if choice_answer[i]:
            selected_id = choice_answer[i].id
        else:
            selected_id = ""
        answer_list.append({
            'sjly': '1',
            'stlx': choice_list[i].type,
            'wjid': basic_info['wjid'],
            'wjssrwid': basic_info['wjssrwid'],
            'wjstctid': "",
            'wjstid': choice_list[i].id,
            'xxdalist': [
                selected_id
            ]
        })
    for q in other_list:
        answer_list.append({
            'sjly': '1',
            'stlx': q.type,
            'wjid': basic_info['wjid'],
            'wjssrwid': basic_info['wjssrwid'],
            'wjstctid': q.options[0].id if q.options else "",
            'wjstid': q.id,
            'xxdalist': [
                ""
            ]
        })
    ret = {
        'pjidlist': [],
        'pjjglist': [
            {
                'bprdm': basic_info['bprdm'],
                'bprmc': basic_info['bprmc'],
                'kcdm': basic_info['kcdm'],
                'kcmc': basic_info['kcmc'],
                'pjdf': total_score,
                'pjfs': basic_info['pjfs'],
                'pjid': basic_info['pjid'],
                'pjlx': basic_info['pjlx'],
                'pjmap': form_info['pjmap'],
                'pjrdm': basic_info['pjrdm'],
                'pjrjsdm': basic_info['pjrjsdm'],
                'pjrxm': basic_info['pjrxm'],
                'pjsx': 1,
                'rwh': basic_info['rwh'],
                'stzjid': basic_info['stzjid'],
                'wjid': basic_info['wjid'],
                'wjssrwid': basic_info['wjssrwid'],
                'wtjjy': '',
                'xhgs': basic_info['xhgs'],
                'xnxq': basic_info['xnxq'],
                'sfxxpj': '1',
                'sqzt': basic_info['sqzt'],
                'yxfz': basic_info['yxfz'],
                'sdrs': basic_info['sdrs'],
                "zsxz": basic_info['pjrjsdm'],
                'sfnm': '1',
                'pjxxlist': answer_list
            }
        ],
        'pjzt': '1'
    }
    return ret

def get_question_list(form_info):
    ret = []
    for entry in form_info['pjxtWjWjbReturnEntity']['wjzblist'][0]['tklist']:
        q = Question(
            isChoice=entry['tmlx'] == '1',
            type=entry['tmlx'],
            id=entry['tmid'],
            options=[]
        )
        for option in entry.get('tmxxlist', []):
            q.options.append(Option(
                id=option['tmxxid'],
                content=option['xxmc'],
                pts=float(option['xxfz'])
            ))
        q.options.sort(key=lambda x: x.pts, reverse=True)
        ret.append(q)
    return ret

def gen_good_answer(choice_list):
    ret = []
    for q in choice_list:
        ret.append(q.options[0] if q.options else None)
    return ret

def gen_random_answer(choice_list):
    ret = []
    for q in choice_list:
        if q.options:
            selected_option = random.choice(q.options[:3]) if len(q.options) >=3 else random.choice(q.options)
            ret.append(selected_option)
        else:
            ret.append(None)
    return ret

def gen_worst_passing_answer(choice_list):
    ret = []
    for q in choice_list:
        if q.options:
            ret.append(q.options[2] if len(q.options) >=3 else q.options[-1])
        else:
            ret.append(None)
    return ret

def enforce_rules(choice_answer, choice_list):
    # 规则1：不能全选同一个选项
    selected_contents = [option.content for option in choice_answer if option]
    if len(set(selected_contents)) == 1:
        for i, option in enumerate(choice_answer):
            # 某些题目可能不存在可选项，此时 choice_answer 中为 None
            if option and option.content != '中等':
                for opt in choice_list[i].options:
                    if opt.content != option.content:
                        choice_answer[i] = opt
                        break
                break
    # 规则2：前五道题中至少有一道选择“合格以上”（中等、良好、优秀）
    count_passing = sum(1 for option in choice_answer[:5] if option and option.content in ['中等', '良好', '优秀'])
    if count_passing == 0:
        for i in range(5):
            if choice_answer[i]:
                for opt in choice_list[i].options:
                    if opt.content == '中等':
                        choice_answer[i] = opt
                        break
                break
