import { useEffect, useRef } from 'react'
import anime from 'animejs'
import styles from './Progress.module.css'

interface ProgressProps {
  current: number
  total: number
}

export function Progress({ current, total }: ProgressProps) {
  const percent = total > 0 ? Math.round((current / total) * 100) : 0
  const fillRef = useRef<HTMLDivElement>(null)
  const percentRef = useRef<HTMLSpanElement>(null)
  const prevPercent = useRef(0)

  useEffect(() => {
    // Animate the progress bar fill
    if (fillRef.current) {
      anime({
        targets: fillRef.current,
        width: `${percent}%`,
        easing: 'easeOutQuart',
        duration: 500,
      })
    }

    // Animate the percentage number
    if (percentRef.current) {
      const obj = { value: prevPercent.current }
      anime({
        targets: obj,
        value: percent,
        round: 1,
        easing: 'easeOutQuart',
        duration: 500,
        update: () => {
          if (percentRef.current) {
            percentRef.current.textContent = `${obj.value}%`
          }
        },
      })
    }

    prevPercent.current = percent
  }, [percent])

  return (
    <div className={styles.wrapper}>
      <div className={styles.bar}>
        <div ref={fillRef} className={styles.fill} style={{ width: 0 }}>
          <div className={styles.glow} />
        </div>
        {/* Animated particles */}
        {percent > 0 && percent < 100 && (
          <div className={styles.particles} style={{ left: `${percent}%` }}>
            <span className={styles.particle} />
            <span className={styles.particle} />
            <span className={styles.particle} />
          </div>
        )}
      </div>
      <div className={styles.stats}>
        <span className={styles.count}>
          <span className={styles.current}>{current}</span>
          <span className={styles.separator}>/</span>
          <span className={styles.total}>{total}</span>
        </span>
        <span ref={percentRef} className={styles.percent}>0%</span>
      </div>
    </div>
  )
}
