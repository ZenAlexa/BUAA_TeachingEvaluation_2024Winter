import { useEffect, useRef, useState } from 'react'
import anime from 'animejs'
import { Check, X, Info, AlertCircle } from 'lucide-react'
import styles from './Toast.module.css'

export interface ToastData {
  id: number
  message: string
  type: 'success' | 'error' | 'info' | 'warning'
}

interface ToastProps {
  toast: ToastData
  onClose: (id: number) => void
}

const icons = {
  success: Check,
  error: X,
  info: Info,
  warning: AlertCircle,
}

export function Toast({ toast, onClose }: ToastProps) {
  const toastRef = useRef<HTMLDivElement>(null)
  const progressRef = useRef<HTMLDivElement>(null)
  const [isExiting, setIsExiting] = useState(false)

  useEffect(() => {
    // Entrance animation
    if (toastRef.current) {
      anime({
        targets: toastRef.current,
        translateX: [100, 0],
        opacity: [0, 1],
        easing: 'easeOutExpo',
        duration: 400,
      })
    }

    // Progress bar animation
    if (progressRef.current) {
      anime({
        targets: progressRef.current,
        width: ['100%', '0%'],
        easing: 'linear',
        duration: 3000,
      })
    }

    // Auto-close timer
    const timer = setTimeout(() => {
      handleClose()
    }, 3000)

    return () => clearTimeout(timer)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleClose = () => {
    if (isExiting) return
    setIsExiting(true)

    if (toastRef.current) {
      anime({
        targets: toastRef.current,
        translateX: [0, 100],
        opacity: [1, 0],
        easing: 'easeInExpo',
        duration: 300,
        complete: () => onClose(toast.id),
      })
    } else {
      onClose(toast.id)
    }
  }

  const Icon = icons[toast.type]

  return (
    <div
      ref={toastRef}
      className={`${styles.toast} ${styles[toast.type]}`}
      onClick={handleClose}
      role="alert"
      style={{ opacity: 0 }}
    >
      <div className={styles.iconWrapper}>
        <Icon size={16} />
      </div>
      <span className={styles.message}>{toast.message}</span>
      <button className={styles.closeButton} onClick={handleClose} aria-label="Close">
        <X size={14} />
      </button>
      <div ref={progressRef} className={styles.progress} />
    </div>
  )
}

interface ToastContainerProps {
  toasts: ToastData[]
  onClose: (id: number) => void
}

export function ToastContainer({ toasts, onClose }: ToastContainerProps) {
  return (
    <div className={styles.container} aria-live="polite">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onClose={onClose} />
      ))}
    </div>
  )
}
