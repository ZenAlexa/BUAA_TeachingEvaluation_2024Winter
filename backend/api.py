"""
API bridge between frontend and backend
Exposes Python methods to JavaScript via pywebview

Version: 1.2.0
- Fixed: Main thread blocking causing app freeze
- Fixed: Added request timeouts to prevent hangs
- Fixed: Thread-safe frontend callbacks
- Improved: Better error handling and logging
"""

import logging
import threading
import time
import webbrowser
from typing import List, Dict, Any, Optional, Callable
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from evaluator import fill_form

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Request configuration
REQUEST_TIMEOUT = (10, 30)  # (connect timeout, read timeout)
MAX_RETRIES = 3
RETRY_BACKOFF = 0.5
EVALUATION_DELAY = 0.8  # Delay between evaluations (seconds)


def create_session() -> requests.Session:
    """Create a requests session with retry logic and connection pooling"""
    session = requests.Session()

    # Configure retry strategy
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=10
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Set default headers
    session.headers.update({
        'User-Agent': 'BUAA-Evaluation/1.2.0',
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })

    return session


class EvaluationAPI:
    """API class exposed to JavaScript frontend

    Thread-safe implementation with non-blocking evaluation process.
    """

    BASE_URL = "https://spoc.buaa.edu.cn/pjxt/"
    LOGIN_URL = f"https://sso.buaa.edu.cn/login?service={quote(BASE_URL, 'utf-8')}cas"
    GITHUB_URL = "https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter"

    def __init__(self):
        self.session = create_session()
        self.window = None
        self._evaluation_thread: Optional[threading.Thread] = None
        self._stop_evaluation = threading.Event()
        self._lock = threading.Lock()

    def set_window(self, window) -> None:
        """Set reference to pywebview window"""
        with self._lock:
            self.window = window

    def _safe_request(
        self,
        method: str,
        url: str,
        timeout: tuple = REQUEST_TIMEOUT,
        **kwargs
    ) -> Optional[requests.Response]:
        """Make a request with timeout and error handling"""
        try:
            response = self.session.request(
                method,
                url,
                timeout=timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code}: {url}")
            return None
        except Exception as e:
            logger.error(f"Request failed: {url} - {e}")
            return None

    def _get_login_token(self) -> Optional[str]:
        """Fetch login token from SSO page"""
        response = self._safe_request('GET', self.LOGIN_URL)
        if not response:
            return None

        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            token_input = soup.find('input', {'name': 'execution'})
            return token_input['value'] if token_input else None
        except Exception as e:
            logger.error(f"Failed to parse login token: {e}")
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
        if not username or not password:
            return {'success': False, 'message': 'Username and password required'}

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

            response = self._safe_request(
                'POST',
                self.LOGIN_URL,
                data=payload,
                allow_redirects=True
            )

            if not response:
                return {'success': False, 'message': 'Login request failed'}

            # Check for successful login indicator
            if '未评价不可查看课表' in response.text:
                logger.info(f"Login successful for user: {username}")
                return {'success': True, 'message': 'Login successful'}

            return {'success': False, 'message': 'Invalid credentials'}

        except Exception as e:
            logger.error(f"Login error: {e}")
            return {'success': False, 'message': str(e)}

    def get_task_info(self) -> Dict[str, Any]:
        """
        Get current evaluation task information

        Returns:
            Dict with task details or error message
        """
        try:
            url = f"{self.BASE_URL}personnelEvaluation/listObtainPersonnelEvaluationTasks"
            response = self._safe_request(
                'GET',
                url,
                params={'pageNum': 1, 'pageSize': 1}
            )

            if not response:
                return {'success': False, 'message': 'Failed to get task info'}

            data = response.json()
            if data.get('result', {}).get('total', 0) == 0:
                return {'success': False, 'message': 'No active tasks'}

            task = data['result']['list'][0]
            return {
                'success': True,
                'task_id': task['rwid'],
                'task_name': task['rwmc']
            }

        except Exception as e:
            logger.error(f"Get task info error: {e}")
            return {'success': False, 'message': str(e)}

    def _get_questionnaires(self, task_id: str) -> List[Dict]:
        """Get questionnaire list for a task"""
        url = f"{self.BASE_URL}evaluationMethodSix/getQuestionnaireListToTask"
        response = self._safe_request(
            'GET',
            url,
            params={'rwid': task_id, 'pageNum': 1, 'pageSize': 999}
        )

        if not response:
            return []

        try:
            return response.json().get('result', [])
        except Exception:
            return []

    def _set_questionnaire_mode(self, questionnaire: Dict) -> bool:
        """Set questionnaire to evaluation mode"""
        try:
            msid = questionnaire.get('msid')
            if msid in ['1', '2']:
                endpoint = 'reviseQuestionnairePattern'
            elif msid is None:
                endpoint = 'confirmQuestionnairePattern'
            else:
                return True  # No action needed

            url = f"{self.BASE_URL}evaluationMethodSix/{endpoint}"
            response = self._safe_request(
                'POST',
                url,
                json={
                    'wjid': questionnaire['wjid'],
                    'msid': 1,
                    'rwid': questionnaire['rwid']
                }
            )
            return response is not None
        except Exception as e:
            logger.error(f"Set questionnaire mode error: {e}")
            return False

    def _get_courses(self, questionnaire_id: str) -> List[Dict]:
        """Get course list for a questionnaire"""
        url = f"{self.BASE_URL}evaluationMethodSix/getRequiredReviewsData"
        response = self._safe_request(
            'GET',
            url,
            params={'sfyp': 0, 'wjid': questionnaire_id, 'pageNum': 1, 'pageSize': 999}
        )

        if not response:
            return []

        try:
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
            response = self._safe_request('GET', url)

            if not response:
                return False

            topics = response.json().get('result', [])
            if not topics:
                return False

            # Generate and submit evaluation
            submission = fill_form(topics[0], method)
            submit_url = f"{self.BASE_URL}evaluationMethodSix/submitSaveEvaluation"
            submit_response = self._safe_request('POST', submit_url, json=submission)

            if not submit_response:
                return False

            return submit_response.json().get('msg') == '成功'

        except Exception as e:
            logger.error(f"Evaluate course error: {e}")
            return False

    def _python_to_js(self, value: Any) -> str:
        """
        Convert Python value to JavaScript literal string.

        Handles:
        - bool: True -> 'true', False -> 'false'
        - None: -> 'null'
        - str: -> quoted string with escaped characters
        - numbers: -> as-is
        - lists/dicts: -> JSON
        """
        import json
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, str):
            # Use json.dumps to properly escape strings
            return json.dumps(value, ensure_ascii=False)
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            # For complex types, use JSON serialization
            return json.dumps(value, ensure_ascii=False)

    def _call_frontend(self, func: str, *args) -> None:
        """Execute JavaScript function in frontend (thread-safe)"""
        with self._lock:
            if self.window:
                try:
                    args_str = ', '.join(self._python_to_js(arg) for arg in args)
                    js_code = f"{func}({args_str})"
                    logger.debug(f"Calling frontend: {js_code}")
                    # Use evaluate_js which is thread-safe in pywebview >= 4.0
                    self.window.evaluate_js(js_code)
                except Exception as e:
                    logger.error(f"Frontend callback error: {e}")

    def _run_evaluation(
        self,
        method: str,
        special_teachers: List[str]
    ) -> None:
        """
        Internal evaluation process (runs in background thread)

        Args:
            method: Evaluation method
            special_teachers: List of teachers for special evaluation
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
                if self._stop_evaluation.is_set():
                    return

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
            special_set = set(special_teachers) if special_teachers else set()

            # Process special teachers first
            if special_set:
                self._call_frontend('addLog', 'info', '-- Special Teachers --')
                for course in pending_courses:
                    if self._stop_evaluation.is_set():
                        return

                    teacher = course.get('pjrxm', 'Unknown')
                    if teacher in special_set:
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
                        time.sleep(EVALUATION_DELAY)

            # Process remaining teachers
            self._call_frontend('addLog', 'info', '-- Other Teachers --')
            for course in pending_courses:
                if self._stop_evaluation.is_set():
                    return

                teacher = course.get('pjrxm', 'Unknown')
                if teacher not in special_set:
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
                    time.sleep(EVALUATION_DELAY)

            self._call_frontend('showComplete')
            logger.info(f"Evaluation completed: {current}/{total} courses")

        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            self._call_frontend('showError', str(e))

    def start_evaluation(self, method: str, special_teachers: List[str]) -> None:
        """
        Start the evaluation process (non-blocking)

        Args:
            method: Evaluation method ('good', 'random', 'worst_passing')
            special_teachers: List of teachers to evaluate with minimum passing

        Note:
            This method returns immediately and runs evaluation in a background thread.
            Progress updates are sent via frontend callbacks.
        """
        # Stop any existing evaluation
        self.stop_evaluation()

        # Reset stop flag
        self._stop_evaluation.clear()

        # Start evaluation in background thread
        self._evaluation_thread = threading.Thread(
            target=self._run_evaluation,
            args=(method, special_teachers),
            daemon=True,
            name="EvaluationThread"
        )
        self._evaluation_thread.start()
        logger.info(f"Started evaluation with method: {method}")

    def stop_evaluation(self) -> None:
        """Stop the current evaluation process"""
        if self._evaluation_thread and self._evaluation_thread.is_alive():
            self._stop_evaluation.set()
            self._evaluation_thread.join(timeout=2.0)
            logger.info("Evaluation stopped")

    def open_github(self) -> None:
        """Open project GitHub page in browser"""
        try:
            webbrowser.open(self.GITHUB_URL)
        except Exception as e:
            logger.error(f"Failed to open GitHub: {e}")
