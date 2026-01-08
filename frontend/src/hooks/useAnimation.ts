import { useEffect, useRef, type RefObject } from 'react'
import anime from 'animejs'

type AnimeParams = anime.AnimeParams

/**
 * Hook for creating entrance animations on elements
 */
export function useEntranceAnimation<T extends HTMLElement>(
  options: AnimeParams = {},
  deps: unknown[] = []
): RefObject<T> {
  const ref = useRef<T>(null)
  const hasAnimated = useRef(false)

  useEffect(() => {
    if (!ref.current || hasAnimated.current) return
    hasAnimated.current = true

    anime({
      targets: ref.current,
      opacity: [0, 1],
      translateY: [20, 0],
      easing: 'easeOutCubic',
      duration: 600,
      ...options,
    })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return ref as RefObject<T>
}

/**
 * Hook for staggered children animations
 */
export function useStaggerAnimation<T extends HTMLElement>(
  selector: string,
  options: AnimeParams = {},
  deps: unknown[] = []
): RefObject<T> {
  const ref = useRef<T>(null)
  const hasAnimated = useRef(false)

  useEffect(() => {
    if (!ref.current || hasAnimated.current) return
    hasAnimated.current = true

    const elements = ref.current.querySelectorAll(selector)
    if (elements.length === 0) return

    anime({
      targets: elements,
      opacity: [0, 1],
      translateY: [15, 0],
      easing: 'easeOutQuart',
      duration: 500,
      delay: anime.stagger(60, { start: 100 }),
      ...options,
    })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return ref as RefObject<T>
}

/**
 * Hook for hover scale animation
 */
export function useHoverAnimation<T extends HTMLElement>(
  scale: number = 1.02
): {
  ref: RefObject<T>
  onMouseEnter: () => void
  onMouseLeave: () => void
} {
  const ref = useRef<T>(null)
  const animation = useRef<anime.AnimeInstance | null>(null)

  const onMouseEnter = () => {
    if (!ref.current) return
    animation.current?.pause()
    animation.current = anime({
      targets: ref.current,
      scale: scale,
      easing: 'easeOutCubic',
      duration: 200,
    })
  }

  const onMouseLeave = () => {
    if (!ref.current) return
    animation.current?.pause()
    animation.current = anime({
      targets: ref.current,
      scale: 1,
      easing: 'easeOutCubic',
      duration: 200,
    })
  }

  return { ref: ref as RefObject<T>, onMouseEnter, onMouseLeave }
}

/**
 * Hook for press/tap animation
 */
export function usePressAnimation<T extends HTMLElement>(): {
  ref: RefObject<T>
  onMouseDown: () => void
  onMouseUp: () => void
} {
  const ref = useRef<T>(null)

  const onMouseDown = () => {
    if (!ref.current) return
    anime({
      targets: ref.current,
      scale: 0.97,
      easing: 'easeOutCubic',
      duration: 100,
    })
  }

  const onMouseUp = () => {
    if (!ref.current) return
    anime({
      targets: ref.current,
      scale: 1,
      easing: 'easeOutElastic(1, .5)',
      duration: 400,
    })
  }

  return { ref: ref as RefObject<T>, onMouseDown, onMouseUp }
}

/**
 * Hook for number counting animation
 */
export function useCountAnimation(
  value: number,
  duration: number = 800
): RefObject<HTMLElement> {
  const ref = useRef<HTMLElement>(null)
  const prevValue = useRef(0)

  useEffect(() => {
    if (!ref.current) return

    const obj = { value: prevValue.current }
    anime({
      targets: obj,
      value: value,
      round: 1,
      easing: 'easeOutQuart',
      duration: duration,
      update: () => {
        if (ref.current) {
          ref.current.textContent = String(obj.value)
        }
      },
    })
    prevValue.current = value
  }, [value, duration])

  return ref as RefObject<HTMLElement>
}

/**
 * Hook for progress bar animation
 */
export function useProgressAnimation(
  percent: number,
  duration: number = 500
): RefObject<HTMLElement> {
  const ref = useRef<HTMLElement>(null)

  useEffect(() => {
    if (!ref.current) return

    anime({
      targets: ref.current,
      width: `${percent}%`,
      easing: 'easeOutQuart',
      duration: duration,
    })
  }, [percent, duration])

  return ref as RefObject<HTMLElement>
}

/**
 * Animate element in
 */
export function animateIn(
  element: HTMLElement | null,
  options: AnimeParams = {}
): anime.AnimeInstance | null {
  if (!element) return null

  return anime({
    targets: element,
    opacity: [0, 1],
    translateY: [20, 0],
    easing: 'easeOutCubic',
    duration: 500,
    ...options,
  })
}

/**
 * Animate element out
 */
export function animateOut(
  element: HTMLElement | null,
  options: AnimeParams = {}
): Promise<void> {
  return new Promise((resolve) => {
    if (!element) {
      resolve()
      return
    }

    anime({
      targets: element,
      opacity: [1, 0],
      translateY: [0, -10],
      easing: 'easeInCubic',
      duration: 300,
      ...options,
      complete: () => resolve(),
    })
  })
}

/**
 * Shake animation for errors
 */
export function animateShake(element: HTMLElement | null): anime.AnimeInstance | null {
  if (!element) return null

  return anime({
    targets: element,
    translateX: [-8, 8, -6, 6, -4, 4, -2, 2, 0],
    easing: 'easeInOutQuad',
    duration: 500,
  })
}

/**
 * Pulse animation
 */
export function animatePulse(element: HTMLElement | null): anime.AnimeInstance | null {
  if (!element) return null

  return anime({
    targets: element,
    scale: [1, 1.05, 1],
    easing: 'easeInOutQuad',
    duration: 400,
  })
}

/**
 * Success checkmark animation
 */
export function animateSuccess(element: HTMLElement | null): anime.AnimeInstance | null {
  if (!element) return null

  return anime({
    targets: element,
    scale: [0, 1.2, 1],
    opacity: [0, 1],
    easing: 'easeOutElastic(1, .6)',
    duration: 800,
  })
}
