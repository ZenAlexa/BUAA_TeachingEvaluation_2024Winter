/**
 * Language toggle switch component
 */

import { useI18n } from '@/i18n'
import styles from './LanguageSwitch.module.css'

export function LanguageSwitch() {
  const { locale, toggleLocale } = useI18n()

  return (
    <button
      className={styles.switch}
      onClick={toggleLocale}
      aria-label="Toggle language"
      title={locale === 'en' ? '切换到中文' : 'Switch to English'}
    >
      <span className={`${styles.option} ${locale === 'en' ? styles.active : ''}`}>EN</span>
      <span className={styles.divider}>/</span>
      <span className={`${styles.option} ${locale === 'zh' ? styles.active : ''}`}>中</span>
    </button>
  )
}
