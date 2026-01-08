import { useEffect } from 'react'
import { Check, X, Info } from 'lucide-react'
import styles from './Toast.module.css'

export interface ToastData {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

interface ToastProps {
  toast: ToastData
  onClose: (id: number) => void
}

const icons = {
  success: Check,
  error: X,
  info: Info,
}

export function Toast({ toast, onClose }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(toast.id)
    }, 3000)

    return () => clearTimeout(timer)
  }, [toast.id, onClose])

  const Icon = icons[toast.type]

  return (
    <div className={`${styles.toast} ${styles[toast.type]}`}>
      <Icon size={16} />
      {toast.message}
    </div>
  )
}

interface ToastContainerProps {
  toasts: ToastData[]
  onClose: (id: number) => void
}

export function ToastContainer({ toasts, onClose }: ToastContainerProps) {
  return (
    <div className={styles.container}>
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onClose={onClose} />
      ))}
    </div>
  )
}
