import { useEffect, useRef } from 'react'
import anime from 'animejs'
import styles from './Logo.module.css'

interface LogoProps {
  size?: number
  animate?: boolean
  className?: string
}

export function Logo({ size = 32, animate = true, className = '' }: LogoProps) {
  const logoRef = useRef<SVGSVGElement>(null)
  const hasAnimated = useRef(false)

  useEffect(() => {
    if (!animate || hasAnimated.current || !logoRef.current) return
    hasAnimated.current = true

    anime({
      targets: logoRef.current.querySelectorAll('.animate-path'),
      strokeDashoffset: [anime.setDashoffset, 0],
      easing: 'easeInOutQuart',
      duration: 1200,
      delay: anime.stagger(100),
    })

    anime({
      targets: logoRef.current.querySelectorAll('.animate-fill'),
      opacity: [0, 1],
      scale: [0.8, 1],
      easing: 'easeOutElastic(1, .8)',
      duration: 800,
      delay: anime.stagger(80, { start: 400 }),
    })
  }, [animate])

  return (
    <svg
      ref={logoRef}
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`${styles.logo} ${className}`}
    >
      <defs>
        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#ffffff" />
          <stop offset="100%" stopColor="#a3a3a3" />
        </linearGradient>
      </defs>

      <rect
        x="4"
        y="4"
        width="56"
        height="56"
        fill="#0a0a0a"
        stroke="#262626"
        strokeWidth="1"
        className="animate-fill"
        style={{ transformOrigin: 'center' }}
      />

      <g className="animate-fill" style={{ transformOrigin: 'center' }}>
        <path
          d="M20 24L26 30L36 18"
          stroke="url(#logoGradient)"
          strokeWidth="3"
          strokeLinecap="square"
          strokeLinejoin="miter"
          fill="none"
          className="animate-path"
        />

        <rect
          x="20"
          y="34"
          width="24"
          height="3"
          fill="#404040"
          className="animate-fill"
          style={{ transformOrigin: 'center' }}
        />

        <rect
          x="20"
          y="42"
          width="16"
          height="3"
          fill="#404040"
          className="animate-fill"
          style={{ transformOrigin: 'center' }}
        />
      </g>

      <rect
        x="47"
        y="17"
        width="6"
        height="6"
        fill="url(#logoGradient)"
        className="animate-fill"
        style={{ transformOrigin: 'center' }}
      />
      <rect
        x="48"
        y="34"
        width="4"
        height="4"
        fill="#525252"
        className="animate-fill"
        style={{ transformOrigin: 'center' }}
      />
      <rect
        x="48"
        y="42"
        width="4"
        height="4"
        fill="#525252"
        className="animate-fill"
        style={{ transformOrigin: 'center' }}
      />
    </svg>
  )
}
