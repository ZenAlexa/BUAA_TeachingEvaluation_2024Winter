/**
 * Application translations for internationalization
 */

export type Locale = 'en' | 'zh'

export interface Translations {
  // Header
  appName: string

  // Login
  loginTitle: string
  loginSubtitle: string
  username: string
  usernamePlaceholder: string
  password: string
  passwordPlaceholder: string
  continue: string
  loading: string

  // Settings
  settingsTitle: string
  settingsSubtitle: string
  method: string
  methodGood: string
  methodGoodDesc: string
  methodRandom: string
  methodRandomDesc: string
  methodMinPass: string
  methodMinPassDesc: string
  defaultBadge: string
  specialTeachers: string
  specialTeachersHint: string
  specialTeachersPlaceholder: string
  start: string

  // Progress
  progressTitle: string

  // Complete
  completeTitle: string
  completeSubtitle: string
  courses: string
  teachers: string

  // Messages
  enterCredentials: string
  loginSuccess: string
  loginFailed: string
  loginError: string
  taskFailed: string
  startError: string
  allEvaluated: string
  specialTeachersSection: string
  otherTeachersSection: string
  evaluationFailed: string

  // Footer
  footer: string
}

export const translations: Record<Locale, Translations> = {
  en: {
    // Header
    appName: 'BUAA Eval',

    // Login
    loginTitle: 'Login',
    loginSubtitle: 'Unified authentication',
    username: 'Username',
    usernamePlaceholder: 'Student ID',
    password: 'Password',
    passwordPlaceholder: 'Password',
    continue: 'Continue',
    loading: 'Loading...',

    // Settings
    settingsTitle: 'Settings',
    settingsSubtitle: 'Configure evaluation',
    method: 'Method',
    methodGood: 'Full Score',
    methodGoodDesc: 'Select highest score for each question',
    methodRandom: 'Random',
    methodRandomDesc: 'Random selection from top 3 options',
    methodMinPass: 'Minimum Pass',
    methodMinPassDesc: 'Select third option for each question',
    defaultBadge: 'Default',
    specialTeachers: 'Special Teachers',
    specialTeachersHint: '(optional)',
    specialTeachersPlaceholder: 'Comma separated names',
    start: 'Start',

    // Progress
    progressTitle: 'Progress',

    // Complete
    completeTitle: 'Complete',
    completeSubtitle: 'All courses evaluated',
    courses: 'Courses',
    teachers: 'Teachers',

    // Messages
    enterCredentials: 'Enter username and password',
    loginSuccess: 'Login successful',
    loginFailed: 'Login failed',
    loginError: 'Login error',
    taskFailed: 'Failed to get task',
    startError: 'Error starting',
    allEvaluated: 'All courses already evaluated',
    specialTeachersSection: '-- Special Teachers --',
    otherTeachersSection: '-- Other Teachers --',
    evaluationFailed: 'Failed',

    // Footer
    footer: 'Made with ❤️ for BUAA',
  },
  zh: {
    // Header
    appName: 'BUAA 评教',

    // Login
    loginTitle: '登录',
    loginSubtitle: '统一身份认证',
    username: '用户名',
    usernamePlaceholder: '学号',
    password: '密码',
    passwordPlaceholder: '密码',
    continue: '继续',
    loading: '加载中...',

    // Settings
    settingsTitle: '设置',
    settingsSubtitle: '配置评教选项',
    method: '评价方式',
    methodGood: '满分评价',
    methodGoodDesc: '每题选择最高分选项',
    methodRandom: '随机评价',
    methodRandomDesc: '从前3个选项中随机选择',
    methodMinPass: '最低及格',
    methodMinPassDesc: '每题选择第三个选项',
    defaultBadge: '默认',
    specialTeachers: '特殊教师',
    specialTeachersHint: '(可选)',
    specialTeachersPlaceholder: '用逗号分隔教师姓名',
    start: '开始',

    // Progress
    progressTitle: '进度',

    // Complete
    completeTitle: '完成',
    completeSubtitle: '所有课程已评价',
    courses: '课程',
    teachers: '教师',

    // Messages
    enterCredentials: '请输入用户名和密码',
    loginSuccess: '登录成功',
    loginFailed: '登录失败',
    loginError: '登录错误',
    taskFailed: '获取任务失败',
    startError: '启动错误',
    allEvaluated: '所有课程已完成评价',
    specialTeachersSection: '-- 特殊教师 --',
    otherTeachersSection: '-- 其他教师 --',
    evaluationFailed: '失败',

    // Footer
    footer: '为 BUAA 用 ❤️ 制作',
  },
}
