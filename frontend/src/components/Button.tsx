import { type ButtonHTMLAttributes, type ReactNode, useRef } from 'react'
import anime from 'animejs'
import styles from './Button.module.css'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  children: ReactNode
}

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  children,
  className = '',
  onClick,
  ...props
}: ButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null)
  const rippleRef = useRef<HTMLSpanElement>(null)

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled || loading) return

    // Ripple effect
    if (buttonRef.current && rippleRef.current) {
      const rect = buttonRef.current.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top

      rippleRef.current.style.left = `${x}px`
      rippleRef.current.style.top = `${y}px`

      anime({
        targets: rippleRef.current,
        scale: [0, 2.5],
        opacity: [0.4, 0],
        easing: 'easeOutExpo',
        duration: 600,
      })
    }

    // Press animation
    anime({
      targets: buttonRef.current,
      scale: [1, 0.97, 1],
      easing: 'easeOutQuad',
      duration: 200,
    })

    onClick?.(e)
  }

  return (
    <button
      ref={buttonRef}
      className={`${styles.button} ${styles[variant]} ${styles[size]} ${className}`}
      disabled={disabled || loading}
      onClick={handleClick}
      {...props}
    >
      <span className={styles.ripple} ref={rippleRef} />
      {loading ? (
        <span className={styles.loader}>
          <span className={styles.loaderDot} />
          <span className={styles.loaderDot} />
          <span className={styles.loaderDot} />
        </span>
      ) : (
        <span className={styles.content}>{children}</span>
      )}
    </button>
  )
}
