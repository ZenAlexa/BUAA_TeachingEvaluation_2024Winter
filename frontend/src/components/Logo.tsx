import { useEffect, useRef } from 'react'
import anime from 'animejs'
import styles from './Logo.module.css'

interface LogoProps {
  size?: number
  animate?: boolean
  className?: string
}

/**
 * SVG Logo component with optional entrance animation
 * BUAA-inspired design with modern geometric elements
 */
export function Logo({ size = 32, animate = true, className = '' }: LogoProps) {
  const logoRef = useRef<SVGSVGElement>(null)
  const hasAnimated = useRef(false)

  useEffect(() => {
    if (!animate || hasAnimated.current || !logoRef.current) return
    hasAnimated.current = true

    // Entrance animation
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
      {/* Background circle with gradient */}
      <defs>
        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#3b82f6" />
          <stop offset="100%" stopColor="#1d4ed8" />
        </linearGradient>
        <linearGradient id="glowGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#60a5fa" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
        </linearGradient>
      </defs>

      {/* Outer glow */}
      <circle
        cx="32"
        cy="32"
        r="30"
        fill="url(#glowGradient)"
        className="animate-fill"
        style={{ transformOrigin: 'center' }}
      />

      {/* Main background */}
      <rect
        x="4"
        y="4"
        width="56"
        height="56"
        rx="12"
        fill="#0a0a0a"
        stroke="#262626"
        strokeWidth="1"
        className="animate-fill"
        style={{ transformOrigin: 'center' }}
      />

      {/* Geometric pattern - represents evaluation/checklist */}
      <g className="animate-fill" style={{ transformOrigin: 'center' }}>
        {/* Top check mark */}
        <path
          d="M20 24L26 30L36 18"
          stroke="url(#logoGradient)"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
          className="animate-path"
        />

        {/* Middle line */}
        <rect
          x="20"
          y="34"
          width="24"
          height="3"
          rx="1.5"
          fill="#404040"
          className="animate-fill"
          style={{ transformOrigin: 'center' }}
        />

        {/* Bottom line */}
        <rect
          x="20"
          y="42"
          width="16"
          height="3"
          rx="1.5"
          fill="#404040"
          className="animate-fill"
          style={{ transformOrigin: 'center' }}
        />
      </g>

      {/* Accent dots */}
      <circle
        cx="50"
        cy="20"
        r="3"
        fill="url(#logoGradient)"
        className="animate-fill"
        style={{ transformOrigin: 'center' }}
      />
      <circle
        cx="50"
        cy="36"
        r="2"
        fill="#525252"
        className="animate-fill"
        style={{ transformOrigin: 'center' }}
      />
      <circle
        cx="50"
        cy="44"
        r="2"
        fill="#525252"
        className="animate-fill"
        style={{ transformOrigin: 'center' }}
      />
    </svg>
  )
}
