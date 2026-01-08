import { useState, useCallback, useMemo } from 'react'
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
  type LogEntry,
  type ToastData,
} from '@/components'
import type { EvaluationMethod } from '@/types/api'
import styles from './App.module.css'

type AppState = 'login' | 'settings' | 'progress' | 'complete'

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

  const showToast = useCallback((message: string, type: ToastData['type'] = 'info') => {
    const id = Date.now()
    setToasts((prev) => [...prev, { id, message, type }])
  }, [])

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const addLog = useCallback((type: LogEntry['type'], message: string) => {
    setLogs((prev) => [...prev, { id: Date.now(), type, message }])
  }, [])

  if (typeof window !== 'undefined') {
    (window as any).updateProgress = (current: number, total: number, course: string, teacher: string, special: boolean) => {
      setProgress({ current, total })
      addLog('success', `${course} - ${teacher}${special ? ' (min)' : ''}`)
      setStats((prev) => ({
        courses: prev.courses + 1,
        teachers: prev.teachers + 1,
      }))
    }
    ;(window as any).showComplete = () => {
      setState('complete')
    }
    ;(window as any).showError = (message: string) => {
      showToast(message, 'error')
      setState('settings')
      setLoading(false)
    }
    ;(window as any).addLog = (type: LogEntry['type'], message: string) => {
      addLog(type, message)
    }
  }

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

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <div className={styles.logo}>
          <img src="./logo.png" alt="" className={styles.logoIcon} />
          <span className={styles.logoText}>{t.appName}</span>
        </div>
        <div className={styles.headerRight}>
          <LanguageSwitch />
          <span className={styles.version}>1.1.0</span>
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
              <Button onClick={handleLogin} loading={loading} disabled={!ready}>
                {ready ? t.continue : t.loading}
                {ready && !loading && <ArrowRight size={16} />}
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
          <Card>
            <div className={styles.complete}>
              <div className={styles.completeIcon}>
                <Check size={24} />
              </div>
              <h2 className={styles.completeTitle}>{t.completeTitle}</h2>
              <p className={styles.completeSubtitle}>{t.completeSubtitle}</p>
              <div className={styles.stats}>
                <div className={styles.stat}>
                  <span className={styles.statValue}>{stats.courses}</span>
                  <span className={styles.statLabel}>{t.courses}</span>
                </div>
                <div className={styles.stat}>
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

      <footer className={styles.footer}>
        <span>{t.footer}</span>
      </footer>

      <ToastContainer toasts={toasts} onClose={removeToast} />
    </div>
  )
}
