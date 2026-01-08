import { useState, useCallback, useMemo, useEffect, useRef } from 'react'
import anime from 'animejs'
import { Check, Github, ArrowRight } from 'lucide-react'
import { useApi } from '@/hooks/useApi'
import { useI18n } from '@/i18n'
import {
  Button,
  Input,
  RadioGroup,
  Card,
  Progress,
  LogViewer,
  ToastContainer,
  LanguageSwitch,
  Logo,
  LoadingScreen,
  type LogEntry,
  type ToastData,
} from '@/components'
import type { EvaluationMethod } from '@/types/api'
import styles from './App.module.css'

type AppState = 'login' | 'settings' | 'progress' | 'complete'

// Application version
const APP_VERSION = '1.3.0'

export default function App() {
  const { ready, login, getTaskInfo, startEvaluation, openGithub } = useApi()
  const { t } = useI18n()

  const methodOptions = useMemo(() => [
    { value: 'good' as const, label: t.methodGood, description: t.methodGoodDesc, badge: t.defaultBadge },
    { value: 'random' as const, label: t.methodRandom, description: t.methodRandomDesc },
    { value: 'worst_passing' as const, label: t.methodMinPass, description: t.methodMinPassDesc },
  ], [t])

  const [state, setState] = useState<AppState>('login')
  const [loading, setLoading] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [method, setMethod] = useState<EvaluationMethod>('good')
  const [specialTeachers, setSpecialTeachers] = useState('')
  const [taskName, setTaskName] = useState('')
  const [progress, setProgress] = useState({ current: 0, total: 0 })
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [stats, setStats] = useState({ courses: 0, teachers: 0 })
  const [toasts, setToasts] = useState<ToastData[]>([])

  // Refs for animations
  const headerRef = useRef<HTMLElement>(null)
  const footerRef = useRef<HTMLElement>(null)
  const completeIconRef = useRef<HTMLDivElement>(null)
  const statsRef = useRef<HTMLDivElement>(null)

  // Use refs to avoid stale closures in global callbacks
  const stateRef = useRef({ setState, setProgress, setLogs, setStats, setLoading })

  // Update refs when functions change
  useEffect(() => {
    stateRef.current = { setState, setProgress, setLogs, setStats, setLoading }
  })

  // Header and footer entrance animation
  useEffect(() => {
    if (headerRef.current) {
      anime({
        targets: headerRef.current,
        opacity: [0, 1],
        translateY: [-20, 0],
        easing: 'easeOutQuart',
        duration: 600,
        delay: 100,
      })
    }
    if (footerRef.current) {
      anime({
        targets: footerRef.current,
        opacity: [0, 1],
        easing: 'easeOutQuart',
        duration: 600,
        delay: 400,
      })
    }
  }, [])

  // Complete state animation
  useEffect(() => {
    if (state === 'complete') {
      if (completeIconRef.current) {
        anime({
          targets: completeIconRef.current,
          scale: [0, 1.2, 1],
          opacity: [0, 1],
          easing: 'easeOutElastic(1, .6)',
          duration: 800,
        })
      }
      if (statsRef.current) {
        anime({
          targets: statsRef.current.querySelectorAll('[data-stat]'),
          opacity: [0, 1],
          translateY: [20, 0],
          easing: 'easeOutQuart',
          duration: 500,
          delay: anime.stagger(100, { start: 400 }),
        })
      }
    }
  }, [state])

  const showToast = useCallback((message: string, type: ToastData['type'] = 'info') => {
    const id = Date.now()
    setToasts((prev) => [...prev, { id, message, type }])
  }, [])

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  // Store showToast in ref for global callbacks
  const showToastRef = useRef(showToast)
  useEffect(() => {
    showToastRef.current = showToast
  }, [showToast])

  // Register global callback functions once on mount
  useEffect(() => {
    if (typeof window === 'undefined') return

    // Define global callbacks that Python backend can call
    const windowAny = window as any

    windowAny.updateProgress = (
      current: number,
      total: number,
      course: string,
      teacher: string,
      special: boolean
    ) => {
      stateRef.current.setProgress({ current, total })
      stateRef.current.setLogs((prev) => [
        ...prev,
        { id: Date.now(), type: 'success', message: `${course} - ${teacher}${special ? ' (min)' : ''}` }
      ])
      stateRef.current.setStats((prev) => ({
        courses: prev.courses + 1,
        teachers: prev.teachers + 1,
      }))
    }

    windowAny.showComplete = () => {
      stateRef.current.setState('complete')
      stateRef.current.setLoading(false)
    }

    windowAny.showError = (message: string) => {
      showToastRef.current(message, 'error')
      stateRef.current.setState('settings')
      stateRef.current.setLoading(false)
    }

    windowAny.addLog = (type: LogEntry['type'], message: string) => {
      stateRef.current.setLogs((prev) => [...prev, { id: Date.now(), type, message }])
    }

    // Cleanup on unmount
    return () => {
      delete windowAny.updateProgress
      delete windowAny.showComplete
      delete windowAny.showError
      delete windowAny.addLog
    }
  }, [])

  const handleLogin = async () => {
    if (!username.trim() || !password) {
      showToast(t.enterCredentials, 'error')
      return
    }

    setLoading(true)
    try {
      const result = await login(username, password)
      if (result.success) {
        showToast(t.loginSuccess, 'success')
        setState('settings')
      } else {
        showToast(result.message || t.loginFailed, 'error')
      }
    } catch {
      showToast(t.loginError, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async () => {
    setLoading(true)
    try {
      const taskInfo = await getTaskInfo()
      if (!taskInfo.success) {
        showToast(taskInfo.message || t.taskFailed, 'error')
        setLoading(false)
        return
      }

      setTaskName(taskInfo.task_name || '')
      setState('progress')
      setLogs([])
      setStats({ courses: 0, teachers: 0 })
      setProgress({ current: 0, total: 0 })

      const teachers = specialTeachers
        .split(',')
        .map((name) => name.trim())
        .filter((name) => name)

      await startEvaluation(method, teachers)
    } catch {
      showToast(t.startError, 'error')
      setLoading(false)
    }
  }

  // Show loading screen while API initializes
  if (!ready) {
    return <LoadingScreen text={t.initializing} />
  }

  return (
    <div className={styles.app}>
      <header ref={headerRef} className={styles.header} style={{ opacity: 0 }}>
        <div className={styles.logo}>
          <Logo size={32} animate={true} />
          <span className={styles.logoText}>{t.appName}</span>
        </div>
        <div className={styles.headerRight}>
          <LanguageSwitch />
          <span className={styles.version}>{APP_VERSION}</span>
        </div>
      </header>

      <main className={styles.main}>
        {state === 'login' && (
          <Card title={t.loginTitle} subtitle={t.loginSubtitle}>
            <div className={styles.form}>
              <Input
                label={t.username}
                placeholder={t.usernamePlaceholder}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
              />
              <Input
                label={t.password}
                type="password"
                placeholder={t.passwordPlaceholder}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
              />
              <Button onClick={handleLogin} loading={loading}>
                {t.continue}
                {!loading && <ArrowRight size={16} />}
              </Button>
            </div>
          </Card>
        )}

        {state === 'settings' && (
          <Card title={t.settingsTitle} subtitle={t.settingsSubtitle}>
            <div className={styles.form}>
              <RadioGroup
                label={t.method}
                options={methodOptions}
                value={method}
                onChange={setMethod}
              />
              <Input
                label={t.specialTeachers}
                hint={t.specialTeachersHint}
                placeholder={t.specialTeachersPlaceholder}
                value={specialTeachers}
                onChange={(e) => setSpecialTeachers(e.target.value)}
              />
              <Button onClick={handleStart} loading={loading}>
                {t.start}
                {!loading && <ArrowRight size={16} />}
              </Button>
            </div>
          </Card>
        )}

        {state === 'progress' && (
          <Card title={t.progressTitle} subtitle={taskName}>
            <div className={styles.form}>
              <Progress current={progress.current} total={progress.total} />
              <LogViewer logs={logs} />
            </div>
          </Card>
        )}

        {state === 'complete' && (
          <Card animate={false}>
            <div className={styles.complete}>
              <div ref={completeIconRef} className={styles.completeIcon} style={{ opacity: 0 }}>
                <Check size={24} strokeWidth={3} />
              </div>
              <h2 className={styles.completeTitle}>{t.completeTitle}</h2>
              <p className={styles.completeSubtitle}>{t.completeSubtitle}</p>
              <div ref={statsRef} className={styles.stats}>
                <div className={styles.stat} data-stat>
                  <span className={styles.statValue}>{stats.courses}</span>
                  <span className={styles.statLabel}>{t.courses}</span>
                </div>
                <div className={styles.stat} data-stat>
                  <span className={styles.statValue}>{stats.teachers}</span>
                  <span className={styles.statLabel}>{t.teachers}</span>
                </div>
              </div>
              <Button variant="secondary" onClick={openGithub}>
                <Github size={16} />
                GitHub
              </Button>
            </div>
          </Card>
        )}
      </main>

      <footer ref={footerRef} className={styles.footer} style={{ opacity: 0 }}>
        <span>{t.footer}</span>
      </footer>

      <ToastContainer toasts={toasts} onClose={removeToast} />
    </div>
  )
}
