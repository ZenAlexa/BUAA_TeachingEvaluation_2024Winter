import { type ReactNode, useEffect, useRef } from 'react'
import anime from 'animejs'
import styles from './Card.module.css'

interface CardProps {
  title?: string
  subtitle?: string
  children: ReactNode
  className?: string
  animate?: boolean
}

export function Card({
  title,
  subtitle,
  children,
  className = '',
  animate = true
}: CardProps) {
  const cardRef = useRef<HTMLDivElement>(null)
  const hasAnimated = useRef(false)

  useEffect(() => {
    if (!animate || hasAnimated.current || !cardRef.current) return
    hasAnimated.current = true

    // Card entrance animation
    anime({
      targets: cardRef.current,
      opacity: [0, 1],
      translateY: [30, 0],
      scale: [0.98, 1],
      easing: 'easeOutCubic',
      duration: 500,
    })

    // Stagger children animation
    const children = cardRef.current.querySelectorAll('[data-animate]')
    if (children.length > 0) {
      anime({
        targets: children,
        opacity: [0, 1],
        translateY: [15, 0],
        easing: 'easeOutQuart',
        duration: 400,
        delay: anime.stagger(50, { start: 200 }),
      })
    }
  }, [animate])

  return (
    <div ref={cardRef} className={`${styles.card} ${className}`} style={{ opacity: animate ? 0 : 1 }}>
      {(title || subtitle) && (
        <div className={styles.header} data-animate>
          {title && <h2 className={styles.title}>{title}</h2>}
          {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        </div>
      )}
      <div className={styles.body}>{children}</div>
    </div>
  )
}
