"""
API bridge between frontend and backend
Exposes Python methods to JavaScript via pywebview

Version: 1.5.0
- Added is_ready() for frontend polling (fixes pywebviewready race condition)
- Added mark_ready() called by main.py on DOM loaded
- Simplified thread safety with proper locking
- Removed unused session pre-warming (caused issues)
- All methods are now safe to call from any thread
"""

import json
import logging
import threading
import time
import webbrowser
from typing import List, Dict, Any, Optional
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from evaluator import fill_form

# Configure logging
logger = logging.getLogger(__name__)

# Request configuration
REQUEST_TIMEOUT = (10, 30)  # (connect, read)
MAX_RETRIES = 3
RETRY_BACKOFF = 0.5
EVALUATION_DELAY = 0.8


def _create_session() -> requests.Session:
    """Create HTTP session with retry logic"""
    session = requests.Session()

    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )

    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update({
        'User-Agent': 'BUAA-Evaluation/1.5.0',
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })

    return session


class EvaluationAPI:
    """API class exposed to JavaScript frontend via pywebview"""

    BASE_URL = "https://spoc.buaa.edu.cn/pjxt/"
    LOGIN_URL = f"https://sso.buaa.edu.cn/login?service={quote(BASE_URL, 'utf-8')}cas"
    GITHUB_URL = "https://github.com/ZenAlexa/BUAA_TeachingEvaluation_2024Winter"

    def __init__(self):
        self._window = None
        self._session: Optional[requests.Session] = None
        self._ready = False
        self._evaluation_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Locks for thread safety
        self._lock = threading.RLock()
        self._session_lock = threading.Lock()

    # ========== Ready State Management ==========

    def mark_ready(self) -> None:
        """Called by main.py when DOM is loaded"""
        with self._lock:
            self._ready = True
            logger.info("API marked as ready")

    def is_ready(self) -> bool:
        """
        Check if API is ready - called by frontend via polling.
        This is the PRIMARY mechanism for frontend initialization.
        """
        with self._lock:
            return self._ready

    def set_window(self, window) -> None:
        """Store window reference for JS callbacks"""
        with self._lock:
            self._window = window
            logger.debug("Window reference set")

    # ========== HTTP Session Management ==========

    @property
    def session(self) -> requests.Session:
        """Lazily create session on first use"""
        if self._session is None:
            with self._session_lock:
                if self._session is None:
                    logger.debug("Creating HTTP session")
                    self._session = _create_session()
        return self._session

    def _request(
        self,
        method: str,
        url: str,
        timeout: tuple = REQUEST_TIMEOUT,
        **kwargs
    ) -> Optional[requests.Response]:
        """Make HTTP request with error handling"""
        try:
            resp = self.session.request(method, url, timeout=timeout, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.exceptions.Timeout:
            logger.error(f"Timeout: {url}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error: {url}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP {e.response.status_code}: {url}")
        except Exception as e:
            logger.error(f"Request failed: {url} - {e}")
        return None

    # ========== Authentication ==========

    def _get_login_token(self) -> Optional[str]:
        """Fetch SSO login token"""
        resp = self._request('GET', self.LOGIN_URL)
        if not resp:
            return None
        try:
            soup = BeautifulSoup(resp.text, 'html.parser')
            token = soup.find('input', {'name': 'execution'})
            return token['value'] if token else None
        except Exception as e:
            logger.error(f"Token parse failed: {e}")
            return None

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate with SSO.
        Returns: {success: bool, message: str}
        """
        if not username or not password:
            return {'success': False, 'message': 'Credentials required'}

        try:
            token = self._get_login_token()
            if not token:
                return {'success': False, 'message': 'Failed to get login token'}

            resp = self._request(
                'POST',
                self.LOGIN_URL,
                data={
                    'username': username,
                    'password': password,
                    'execution': token,
                    '_eventId': 'submit',
                    'type': 'username_password',
                    'submit': 'LOGIN'
                },
                allow_redirects=True
            )

            if not resp:
                return {'success': False, 'message': 'Login request failed'}

            if '未评价不可查看课表' in resp.text:
                logger.info(f"Login successful: {username}")
                return {'success': True, 'message': 'Login successful'}

            return {'success': False, 'message': 'Invalid credentials'}

        except Exception as e:
            logger.error(f"Login error: {e}")
            return {'success': False, 'message': str(e)}

    # ========== Task Info ==========

    def get_task_info(self) -> Dict[str, Any]:
        """Get current evaluation task info"""
        try:
            url = f"{self.BASE_URL}personnelEvaluation/listObtainPersonnelEvaluationTasks"
            resp = self._request('GET', url, params={'pageNum': 1, 'pageSize': 1})

            if not resp:
                return {'success': False, 'message': 'Failed to get task info'}

            data = resp.json()
            if data.get('result', {}).get('total', 0) == 0:
                return {'success': False, 'message': 'No active tasks'}

            task = data['result']['list'][0]
            return {
                'success': True,
                'task_id': task['rwid'],
                'task_name': task['rwmc']
            }
        except Exception as e:
            logger.error(f"Task info error: {e}")
            return {'success': False, 'message': str(e)}

    # ========== Evaluation Process ==========

    def _get_questionnaires(self, task_id: str) -> List[Dict]:
        """Get questionnaires for task"""
        url = f"{self.BASE_URL}evaluationMethodSix/getQuestionnaireListToTask"
        resp = self._request('GET', url, params={'rwid': task_id, 'pageNum': 1, 'pageSize': 999})
        if not resp:
            return []
        try:
            return resp.json().get('result', [])
        except Exception:
            return []

    def _set_questionnaire_mode(self, q: Dict) -> bool:
        """Set questionnaire to evaluation mode"""
        try:
            msid = q.get('msid')
            if msid in ['1', '2']:
                endpoint = 'reviseQuestionnairePattern'
            elif msid is None:
                endpoint = 'confirmQuestionnairePattern'
            else:
                return True

            url = f"{self.BASE_URL}evaluationMethodSix/{endpoint}"
            resp = self._request('POST', url, json={
                'wjid': q['wjid'],
                'msid': 1,
                'rwid': q['rwid']
            })
            return resp is not None
        except Exception as e:
            logger.error(f"Set mode error: {e}")
            return False

    def _get_courses(self, qid: str) -> List[Dict]:
        """Get courses for questionnaire"""
        url = f"{self.BASE_URL}evaluationMethodSix/getRequiredReviewsData"
        resp = self._request('GET', url, params={
            'sfyp': 0, 'wjid': qid, 'pageNum': 1, 'pageSize': 999
        })
        if not resp:
            return []
        try:
            return resp.json().get('result', [])
        except Exception:
            return []

    def _evaluate_course(self, course: Dict, method: str) -> bool:
        """Submit evaluation for one course"""
        try:
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

            query = '&'.join(f"{k}={quote(str(v))}" for k, v in params.items())
            url = f"{self.BASE_URL}evaluationMethodSix/getQuestionnaireTopic?{query}"
            resp = self._request('GET', url)

            if not resp:
                return False

            topics = resp.json().get('result', [])
            if not topics:
                return False

            submission = fill_form(topics[0], method)
            submit_url = f"{self.BASE_URL}evaluationMethodSix/submitSaveEvaluation"
            submit_resp = self._request('POST', submit_url, json=submission)

            if not submit_resp:
                return False

            return submit_resp.json().get('msg') == '成功'

        except Exception as e:
            logger.error(f"Evaluate error: {e}")
            return False

    # ========== Frontend Callbacks ==========

    def _to_js(self, value: Any) -> str:
        """Convert Python value to JavaScript literal"""
        if value is None:
            return 'null'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, str):
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, (int, float)):
            return str(value)
        return json.dumps(value, ensure_ascii=False)

    def _call_js(self, func: str, *args) -> None:
        """Call JavaScript function (thread-safe)"""
        with self._lock:
            if not self._window:
                return
            try:
                args_str = ', '.join(self._to_js(arg) for arg in args)
                js = f"{func}({args_str})"
                logger.debug(f"JS call: {js[:100]}")
                self._window.evaluate_js(js)
            except Exception as e:
                logger.error(f"JS call failed: {e}")

    # ========== Evaluation Runner ==========

    def _run_evaluation(self, method: str, special_teachers: List[str]) -> None:
        """Background evaluation thread"""
        try:
            task = self.get_task_info()
            if not task['success']:
                self._call_js('showError', task['message'])
                return

            questionnaires = self._get_questionnaires(task['task_id'])
            if not questionnaires:
                self._call_js('showError', 'No questionnaires found')
                return

            # Collect pending courses
            pending = []
            for q in questionnaires:
                if self._stop_event.is_set():
                    return
                self._set_questionnaire_mode(q)
                for c in self._get_courses(q['wjid']):
                    if c.get('ypjcs') != c.get('xypjcs'):
                        pending.append(c)

            total = len(pending)
            if total == 0:
                self._call_js('addLog', 'info', 'All courses already evaluated')
                self._call_js('showComplete')
                return

            current = 0
            special_set = set(special_teachers) if special_teachers else set()

            # Process special teachers first
            if special_set:
                self._call_js('addLog', 'info', '-- Special Teachers --')
                for course in pending:
                    if self._stop_event.is_set():
                        return
                    teacher = course.get('pjrxm', 'Unknown')
                    if teacher in special_set:
                        success = self._evaluate_course(course, 'worst_passing')
                        current += 1
                        if success:
                            self._call_js('updateProgress', current, total,
                                         course['kcmc'], teacher, True)
                        else:
                            self._call_js('addLog', 'error',
                                         f"Failed: {course['kcmc']} - {teacher}")
                        time.sleep(EVALUATION_DELAY)

            # Process other teachers
            self._call_js('addLog', 'info', '-- Other Teachers --')
            for course in pending:
                if self._stop_event.is_set():
                    return
                teacher = course.get('pjrxm', 'Unknown')
                if teacher not in special_set:
                    success = self._evaluate_course(course, method)
                    current += 1
                    if success:
                        self._call_js('updateProgress', current, total,
                                     course['kcmc'], teacher, False)
                    else:
                        self._call_js('addLog', 'error',
                                     f"Failed: {course['kcmc']} - {teacher}")
                    time.sleep(EVALUATION_DELAY)

            self._call_js('showComplete')
            logger.info(f"Completed: {current}/{total}")

        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            self._call_js('showError', str(e))

    def start_evaluation(self, method: str, special_teachers: List[str]) -> None:
        """Start evaluation (non-blocking)"""
        self.stop_evaluation()
        self._stop_event.clear()

        self._evaluation_thread = threading.Thread(
            target=self._run_evaluation,
            args=(method, special_teachers),
            daemon=True,
            name="Evaluation"
        )
        self._evaluation_thread.start()
        logger.info(f"Started evaluation: {method}")

    def stop_evaluation(self) -> None:
        """Stop current evaluation"""
        if self._evaluation_thread and self._evaluation_thread.is_alive():
            self._stop_event.set()
            self._evaluation_thread.join(timeout=2.0)
            logger.info("Evaluation stopped")

    def open_github(self) -> None:
        """Open GitHub page"""
        try:
            webbrowser.open(self.GITHUB_URL)
        except Exception as e:
            logger.error(f"Open GitHub failed: {e}")
