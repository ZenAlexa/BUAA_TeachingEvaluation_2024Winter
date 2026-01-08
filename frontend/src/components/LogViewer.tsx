import { useRef, useEffect } from 'react'
import { Check, X, Info, AlertTriangle } from 'lucide-react'
import { useI18n } from '@/i18n'
import styles from './LogViewer.module.css'

export interface LogEntry {
  id: number
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
}

interface LogViewerProps {
  logs: LogEntry[]
}

const icons = {
  success: Check,
  error: X,
  info: Info,
  warning: AlertTriangle,
}

export function LogViewer({ logs }: LogViewerProps) {
  const { t } = useI18n()
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [logs])

  return (
    <div className={styles.container} ref={containerRef}>
      {logs.length === 0 ? (
        <div className={styles.empty}>{t.waiting}</div>
      ) : (
        logs.map((log) => {
          const Icon = icons[log.type]
          return (
            <div key={log.id} className={`${styles.entry} ${styles[log.type]}`}>
              <span className={styles.icon}>
                <Icon size={14} />
              </span>
              <span className={styles.message}>{log.message}</span>
            </div>
          )
        })
      )}
    </div>
  )
}
