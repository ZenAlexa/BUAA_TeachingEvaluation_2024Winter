"""
API bridge between frontend and backend
Exposes Python methods to JavaScript via pywebview
"""

import time
import webbrowser
from typing import List, Dict, Any, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from .evaluator import fill_form


class EvaluationAPI:
    """API class exposed to JavaScript frontend"""

    BASE_URL = "https://spoc.buaa.edu.cn/pjxt/"
    LOGIN_URL = f"https://sso.buaa.edu.cn/login?service={quote(BASE_URL, 'utf-8')}cas"
    GITHUB_URL = "https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter"

    def __init__(self):
        self.session = requests.Session()
        self.window = None

    def set_window(self, window) -> None:
        """Set reference to pywebview window"""
        self.window = window

    def _get_login_token(self) -> Optional[str]:
        """Fetch login token from SSO page"""
        try:
            response = self.session.get(self.LOGIN_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            token_input = soup.find('input', {'name': 'execution'})
            return token_input['value'] if token_input else None
        except Exception:
            return None

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate with SSO

        Args:
            username: Student ID
            password: SSO password

        Returns:
            Dict with success status and message
        """
        try:
            token = self._get_login_token()
            if not token:
                return {'success': False, 'message': 'Failed to get login token'}

            payload = {
                'username': username,
                'password': password,
                'execution': token,
                '_eventId': 'submit',
                'type': 'username_password',
                'submit': 'LOGIN'
            }

            response = self.session.post(
                self.LOGIN_URL,
                data=payload,
                allow_redirects=True
            )
            response.raise_for_status()

            # Check for successful login indicator
            if '未评价不可查看课表' in response.text:
                return {'success': True, 'message': 'Login successful'}

            return {'success': False, 'message': 'Invalid credentials'}

        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_task_info(self) -> Dict[str, Any]:
        """
        Get current evaluation task information

        Returns:
            Dict with task details or error message
        """
        try:
            url = f"{self.BASE_URL}personnelEvaluation/listObtainPersonnelEvaluationTasks"
            response = self.session.get(url, params={'pageNum': 1, 'pageSize': 1})
            response.raise_for_status()

            data = response.json()
            if data['result']['total'] == 0:
                return {'success': False, 'message': 'No active tasks'}

            task = data['result']['list'][0]
            return {
                'success': True,
                'task_id': task['rwid'],
                'task_name': task['rwmc']
            }

        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _get_questionnaires(self, task_id: str) -> List[Dict]:
        """Get questionnaire list for a task"""
        try:
            url = f"{self.BASE_URL}evaluationMethodSix/getQuestionnaireListToTask"
            response = self.session.get(url, params={
                'rwid': task_id,
                'pageNum': 1,
                'pageSize': 999
            })
            response.raise_for_status()
            return response.json().get('result', [])
        except Exception:
            return []

    def _set_questionnaire_mode(self, questionnaire: Dict) -> None:
        """Set questionnaire to evaluation mode"""
        try:
            msid = questionnaire.get('msid')
            if msid in ['1', '2']:
                endpoint = 'reviseQuestionnairePattern'
            elif msid is None:
                endpoint = 'confirmQuestionnairePattern'
            else:
                return

            url = f"{self.BASE_URL}evaluationMethodSix/{endpoint}"
            self.session.post(url, json={
                'wjid': questionnaire['wjid'],
                'msid': 1,
                'rwid': questionnaire['rwid']
            })
        except Exception:
            pass

    def _get_courses(self, questionnaire_id: str) -> List[Dict]:
        """Get course list for a questionnaire"""
        try:
            url = f"{self.BASE_URL}evaluationMethodSix/getRequiredReviewsData"
            response = self.session.get(url, params={
                'sfyp': 0,
                'wjid': questionnaire_id,
                'pageNum': 1,
                'pageSize': 999
            })
            response.raise_for_status()
            return response.json().get('result', [])
        except Exception:
            return []

    def _evaluate_course(self, course: Dict, method: str) -> bool:
        """Submit evaluation for a single course"""
        try:
            # Build query params
            params = {
                'rwid': course['rwid'],
                'wjid': course['wjid'],
                'sxz': course['sxz'],
                'pjrdm': course['pjrdm'],
                'pjrmc': course['pjrmc'],
                'bpdm': course['bpdm'],
                'bpmc': course['bpmc'],
                'kcdm': course['kcdm'],
                'kcmc': course['kcmc'],
                'rwh': course['rwh']
            }

            # Get questionnaire topics
            query = '&'.join(f"{k}={quote(str(v))}" for k, v in params.items())
            url = f"{self.BASE_URL}evaluationMethodSix/getQuestionnaireTopic?{query}"
            response = self.session.get(url)
            response.raise_for_status()

            topics = response.json().get('result', [])
            if not topics:
                return False

            # Generate and submit evaluation
            submission = fill_form(topics[0], method)
            submit_url = f"{self.BASE_URL}evaluationMethodSix/submitSaveEvaluation"
            submit_response = self.session.post(submit_url, json=submission)
            submit_response.raise_for_status()

            return submit_response.json().get('msg') == '成功'

        except Exception:
            return False

    def _call_frontend(self, func: str, *args) -> None:
        """Execute JavaScript function in frontend"""
        if self.window:
            args_str = ', '.join(repr(arg) for arg in args)
            self.window.evaluate_js(f"{func}({args_str})")

    def start_evaluation(self, method: str, special_teachers: List[str]) -> None:
        """
        Start the evaluation process

        Args:
            method: Evaluation method ('good', 'random', 'worst_passing')
            special_teachers: List of teachers to evaluate with minimum passing
        """
        try:
            # Get task info
            task_result = self.get_task_info()
            if not task_result['success']:
                self._call_frontend('showError', task_result['message'])
                return

            task_id = task_result['task_id']
            questionnaires = self._get_questionnaires(task_id)

            if not questionnaires:
                self._call_frontend('showError', 'No questionnaires found')
                return

            # Collect all pending courses
            pending_courses = []
            for q in questionnaires:
                self._set_questionnaire_mode(q)
                courses = self._get_courses(q['wjid'])
                for c in courses:
                    # Check if not yet evaluated
                    if c.get('ypjcs') != c.get('xypjcs'):
                        pending_courses.append(c)

            total = len(pending_courses)
            if total == 0:
                self._call_frontend('addLog', 'info', 'All courses already evaluated')
                self._call_frontend('showComplete')
                return

            current = 0

            # Process special teachers first
            if special_teachers:
                self._call_frontend('addLog', 'info', '-- Special Teachers --')
                for course in pending_courses:
                    teacher = course.get('pjrxm', 'Unknown')
                    if teacher in special_teachers:
                        success = self._evaluate_course(course, 'worst_passing')
                        current += 1
                        if success:
                            self._call_frontend(
                                'updateProgress',
                                current, total,
                                course['kcmc'], teacher, True
                            )
                        else:
                            self._call_frontend(
                                'addLog', 'error',
                                f"Failed: {course['kcmc']} - {teacher}"
                            )
                        time.sleep(1)

            # Process remaining teachers
            self._call_frontend('addLog', 'info', '-- Other Teachers --')
            for course in pending_courses:
                teacher = course.get('pjrxm', 'Unknown')
                if teacher not in special_teachers:
                    success = self._evaluate_course(course, method)
                    current += 1
                    if success:
                        self._call_frontend(
                            'updateProgress',
                            current, total,
                            course['kcmc'], teacher, False
                        )
                    else:
                        self._call_frontend(
                            'addLog', 'error',
                            f"Failed: {course['kcmc']} - {teacher}"
                        )
                    time.sleep(1)

            self._call_frontend('showComplete')

        except Exception as e:
            self._call_frontend('showError', str(e))

    def open_github(self) -> None:
        """Open project GitHub page in browser"""
        webbrowser.open(self.GITHUB_URL)
