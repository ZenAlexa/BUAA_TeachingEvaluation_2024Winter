import { useEffect, useRef } from 'react'
import anime from 'animejs'
import { AlertCircle } from 'lucide-react'
import { Logo } from './Logo'
import styles from './LoadingScreen.module.css'

interface LoadingScreenProps {
  text?: string
  error?: string | null
}

export function LoadingScreen({ text = 'Loading...', error }: LoadingScreenProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const textRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      anime({
        targets: containerRef.current,
        opacity: [0, 1],
        duration: 300,
        easing: 'easeOutQuart',
      })
    }

    // Only animate text if no error
    if (textRef.current && !error) {
      anime({
        targets: textRef.current,
        opacity: [0.5, 1, 0.5],
        duration: 1500,
        easing: 'easeInOutSine',
        loop: true,
      })
    }
  }, [error])

  return (
    <div ref={containerRef} className={styles.container} style={{ opacity: 0 }}>
      <div className={styles.content}>
        <Logo size={48} animate={true} />
        {error ? (
          <div className={styles.errorContainer}>
            <AlertCircle size={20} className={styles.errorIcon} />
            <div className={styles.errorText}>{error}</div>
          </div>
        ) : (
          <div ref={textRef} className={styles.text}>{text}</div>
        )}
      </div>
    </div>
  )
}
