import { useEffect, useRef } from 'react'
import anime from 'animejs'
import { Logo } from './Logo'
import styles from './LoadingScreen.module.css'

interface LoadingScreenProps {
  text?: string
}

export function LoadingScreen({ text = 'Loading...' }: LoadingScreenProps) {
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

    if (textRef.current) {
      anime({
        targets: textRef.current,
        opacity: [0.5, 1, 0.5],
        duration: 1500,
        easing: 'easeInOutSine',
        loop: true,
      })
    }
  }, [])

  return (
    <div ref={containerRef} className={styles.container} style={{ opacity: 0 }}>
      <div className={styles.content}>
        <Logo size={48} animate={true} />
        <div ref={textRef} className={styles.text}>{text}</div>
      </div>
    </div>
  )
}
