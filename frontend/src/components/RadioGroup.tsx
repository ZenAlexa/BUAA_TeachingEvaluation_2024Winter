import styles from './RadioGroup.module.css'

interface RadioOption<T extends string> {
  value: T
  label: string
  description: string
  badge?: string
}

interface RadioGroupProps<T extends string> {
  label?: string
  options: RadioOption<T>[]
  value: T
  onChange: (value: T) => void
}

export function RadioGroup<T extends string>({
  label,
  options,
  value,
  onChange,
}: RadioGroupProps<T>) {
  return (
    <div className={styles.wrapper}>
      {label && <span className={styles.label}>{label}</span>}
      <div className={styles.options}>
        {options.map((option) => (
          <label
            key={option.value}
            className={`${styles.option} ${value === option.value ? styles.selected : ''}`}
          >
            <input
              type="radio"
              name="radio-group"
              value={option.value}
              checked={value === option.value}
              onChange={() => onChange(option.value)}
              className={styles.input}
            />
            <div className={styles.content}>
              <span className={styles.optionLabel}>{option.label}</span>
              <span className={styles.description}>{option.description}</span>
            </div>
            {option.badge && (
              <span className={styles.badge}>{option.badge}</span>
            )}
          </label>
        ))}
      </div>
    </div>
  )
}
