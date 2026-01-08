"""
Core evaluation logic module
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class Option:
    """Represents a single answer option"""
    id: str
    content: str
    points: float


@dataclass
class Question:
    """Represents a questionnaire question"""
    is_choice: bool
    type: str
    id: str
    options: List[Option]


def parse_questions(form_data: Dict[str, Any]) -> List[Question]:
    """Parse questions from API response with error handling"""
    questions = []

    try:
        # Navigate through nested structure safely
        wj_entity = form_data.get('pjxtWjWjbReturnEntity')
        if not wj_entity:
            raise ValueError("Missing pjxtWjWjbReturnEntity in form data")

        wjzb_list = wj_entity.get('wjzblist', [])
        if not wjzb_list:
            raise ValueError("Missing wjzblist in form data")

        entries = wjzb_list[0].get('tklist', [])
        if not entries:
            raise ValueError("Missing tklist in form data")

        for entry in entries:
            q = Question(
                is_choice=str(entry.get('tmlx', '')) == '1',
                type=str(entry.get('tmlx', '')),
                id=str(entry.get('tmid', '')),
                options=[]
            )

            for opt in entry.get('tmxxlist', []):
                try:
                    q.options.append(Option(
                        id=str(opt.get('tmxxid', '')),
                        content=str(opt.get('xxmc', '')),
                        points=float(opt.get('xxfz', 0))
                    ))
                except (ValueError, TypeError):
                    # Skip invalid options
                    continue

            # Sort options by points (highest first)
            q.options.sort(key=lambda x: x.points, reverse=True)
            questions.append(q)

    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(f"Failed to parse form data: {e}")

    return questions


def generate_good_answers(questions: List[Question]) -> List[Optional[Option]]:
    """Generate answers selecting highest score for each question"""
    return [q.options[0] if q.options else None for q in questions]


def generate_random_answers(questions: List[Question]) -> List[Optional[Option]]:
    """Generate answers with random selection from top options"""
    answers = []
    for q in questions:
        if q.options:
            # Select from top 3 options
            pool = q.options[:3] if len(q.options) >= 3 else q.options
            answers.append(random.choice(pool))
        else:
            answers.append(None)
    return answers


def generate_passing_answers(questions: List[Question]) -> List[Optional[Option]]:
    """Generate answers selecting minimum passing score"""
    answers = []
    for q in questions:
        if q.options:
            # Select third option (minimum pass) if available
            idx = 2 if len(q.options) >= 3 else len(q.options) - 1
            answers.append(q.options[idx])
        else:
            answers.append(None)
    return answers


def apply_validation_rules(
    answers: List[Optional[Option]],
    questions: List[Question]
) -> None:
    """Apply validation rules to prevent rejection"""
    # Rule 1: Cannot select same option for all questions
    contents = [opt.content for opt in answers if opt]
    if len(set(contents)) == 1:
        for i, opt in enumerate(answers):
            if opt and opt.content != 'Medium':
                for alt in questions[i].options:
                    if alt.content != opt.content:
                        answers[i] = alt
                        break
                break

    # Rule 2: First 5 questions must have at least one passing option
    passing_values = {'Medium', 'Good', 'Excellent'}
    passing_count = sum(
        1 for opt in answers[:5]
        if opt and opt.content in passing_values
    )

    if passing_count == 0:
        for i in range(min(5, len(answers))):
            if answers[i]:
                for opt in questions[i].options:
                    if opt.content == 'Medium':
                        answers[i] = opt
                        break
                break


def build_submission(
    form_data: Dict[str, Any],
    answers: List[Optional[Option]],
    questions: List[Question]
) -> Dict[str, Any]:
    """Build the submission payload with error handling"""
    # Safely get basic info
    pjjgckb = form_data.get('pjxtPjjgPjjgckb', [])
    if len(pjjgckb) < 2:
        raise ValueError("Invalid pjxtPjjgPjjgckb structure")

    basic = pjjgckb[1]
    choice_questions = [q for q in questions if q.is_choice]
    other_questions = [q for q in questions if not q.is_choice]

    # Calculate total score
    total_score = int(sum(
        opt.points for opt in answers if opt
    ))

    # Build answer list
    answer_list = []

    # Choice questions
    for i, q in enumerate(choice_questions):
        answer_list.append({
            'sjly': '1',
            'stlx': q.type,
            'wjid': basic['wjid'],
            'wjssrwid': basic['wjssrwid'],
            'wjstctid': '',
            'wjstid': q.id,
            'xxdalist': [answers[i].id if answers[i] else '']
        })

    # Other questions (text fields)
    for q in other_questions:
        answer_list.append({
            'sjly': '1',
            'stlx': q.type,
            'wjid': basic['wjid'],
            'wjssrwid': basic['wjssrwid'],
            'wjstctid': q.options[0].id if q.options else '',
            'wjstid': q.id,
            'xxdalist': ['']
        })

    return {
        'pjidlist': [],
        'pjjglist': [{
            'bprdm': basic['bprdm'],
            'bprmc': basic['bprmc'],
            'kcdm': basic['kcdm'],
            'kcmc': basic['kcmc'],
            'pjdf': total_score,
            'pjfs': basic['pjfs'],
            'pjid': basic['pjid'],
            'pjlx': basic['pjlx'],
            'pjmap': form_data['pjmap'],
            'pjrdm': basic['pjrdm'],
            'pjrjsdm': basic['pjrjsdm'],
            'pjrxm': basic['pjrxm'],
            'pjsx': 1,
            'rwh': basic['rwh'],
            'stzjid': basic['stzjid'],
            'wjid': basic['wjid'],
            'wjssrwid': basic['wjssrwid'],
            'wtjjy': '',
            'xhgs': basic['xhgs'],
            'xnxq': basic['xnxq'],
            'sfxxpj': '1',
            'sqzt': basic['sqzt'],
            'yxfz': basic['yxfz'],
            'sdrs': basic['sdrs'],
            'zsxz': basic['pjrjsdm'],
            'sfnm': '1',
            'pjxxlist': answer_list
        }],
        'pjzt': '1'
    }


def fill_form(form_data: Dict[str, Any], method: str = 'good') -> Dict[str, Any]:
    """
    Process form data and generate submission payload

    Args:
        form_data: Raw form data from API
        method: Evaluation method ('good', 'random', 'worst_passing')

    Returns:
        Submission payload ready for API
    """
    questions = parse_questions(form_data)
    choice_questions = [q for q in questions if q.is_choice]

    # Generate answers based on method
    if method == 'good':
        answers = generate_good_answers(choice_questions)
    elif method == 'random':
        answers = generate_random_answers(choice_questions)
    elif method == 'worst_passing':
        answers = generate_passing_answers(choice_questions)
    else:
        raise ValueError(f"Unknown method: {method}")

    # Apply validation rules
    apply_validation_rules(answers, choice_questions)

    return build_submission(form_data, answers, questions)
