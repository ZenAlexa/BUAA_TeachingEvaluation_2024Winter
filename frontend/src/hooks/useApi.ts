import { useCallback, useEffect, useRef, useState } from 'react'
import type { PyWebViewAPI, LoginResult, TaskInfo, EvaluationMethod } from '@/types/api'

// Extended window types for pywebview integration
interface PywebviewState {
  apiReady: boolean
  callbacks: Array<() => void>
}

declare global {
  interface Window {
    __pywebviewState?: PywebviewState
    __onPywebviewReady?: (callback: () => void) => void
    __hideInitialLoader?: () => void
  }
}

// Configuration
const POLL_INTERVAL = 100  // ms between polls
const MAX_POLL_TIME = 15000  // 15 seconds max wait

/**
 * Hook to access the pywebview API
 *
 * Uses multiple strategies to ensure reliable initialization:
 * 1. Check if already ready (from index.html early capture)
 * 2. Register callback with __onPywebviewReady
 * 3. Poll api.is_ready() to verify backend is truly ready
 * 4. Timeout fallback after MAX_POLL_TIME
 */
export function useApi() {
  const [ready, setReady] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [api, setApi] = useState<PyWebViewAPI | null>(null)
  const pollRef = useRef<number | null>(null)
  const startTimeRef = useRef<number>(0)

  useEffect(() => {
    let mounted = true
    startTimeRef.current = Date.now()

    // Hide initial loader and set ready state
    const handleReady = (pywebviewApi: PyWebViewAPI) => {
      if (!mounted) return

      console.log('[useApi] API ready, setting state')
      setApi(pywebviewApi)
      setReady(true)

      // Hide the HTML loader
      if (window.__hideInitialLoader) {
        window.__hideInitialLoader()
      }
    }

    // Poll api.is_ready() to verify backend is truly ready
    const startPolling = (pywebviewApi: PyWebViewAPI) => {
      console.log('[useApi] Starting is_ready() polling')

      const poll = async () => {
        if (!mounted) return

        const elapsed = Date.now() - startTimeRef.current
        if (elapsed > MAX_POLL_TIME) {
          console.error('[useApi] Timeout waiting for is_ready()')
          setError('Connection timeout. Please restart the application.')
          // Still try to proceed - maybe it will work
          handleReady(pywebviewApi)
          return
        }

        try {
          const isReady = await pywebviewApi.is_ready()
          if (isReady) {
            console.log('[useApi] Backend confirmed ready via is_ready()')
            handleReady(pywebviewApi)
          } else {
            // Keep polling
            pollRef.current = window.setTimeout(poll, POLL_INTERVAL)
          }
        } catch (e) {
          console.warn('[useApi] is_ready() call failed, retrying...', e)
          pollRef.current = window.setTimeout(poll, POLL_INTERVAL)
        }
      }

      poll()
    }

    // Handle when pywebview API becomes available
    const onApiAvailable = () => {
      if (!mounted) return
      if (!window.pywebview?.api) {
        console.error('[useApi] pywebview.api not found')
        return
      }

      console.log('[useApi] pywebview.api available, starting ready check')
      startPolling(window.pywebview.api)
    }

    // Strategy 1: Check if already ready
    if (window.pywebview?.api) {
      console.log('[useApi] API already available on mount')
      onApiAvailable()
      return
    }

    // Strategy 2: Use the early capture callback from index.html
    if (window.__onPywebviewReady) {
      console.log('[useApi] Registering with __onPywebviewReady')
      window.__onPywebviewReady(onApiAvailable)
    }

    // Strategy 3: Also listen for the event directly (belt and suspenders)
    const handleEvent = () => {
      console.log('[useApi] Received pywebviewready event')
      onApiAvailable()
    }
    window.addEventListener('pywebviewready', handleEvent)

    // Cleanup
    return () => {
      mounted = false
      window.removeEventListener('pywebviewready', handleEvent)
      if (pollRef.current !== null) {
        clearTimeout(pollRef.current)
      }
    }
  }, [])

  // API methods with null checks
  const login = useCallback(
    async (username: string, password: string): Promise<LoginResult> => {
      if (!api) return { success: false, message: 'API not ready' }
      try {
        return await api.login(username, password)
      } catch (e) {
        console.error('[useApi] login error:', e)
        return { success: false, message: 'Login failed' }
      }
    },
    [api]
  )

  const getTaskInfo = useCallback(async (): Promise<TaskInfo> => {
    if (!api) return { success: false, message: 'API not ready' }
    try {
      return await api.get_task_info()
    } catch (e) {
      console.error('[useApi] get_task_info error:', e)
      return { success: false, message: 'Failed to get task info' }
    }
  }, [api])

  const startEvaluation = useCallback(
    async (method: EvaluationMethod, specialTeachers: string[]): Promise<void> => {
      if (!api) return
      try {
        await api.start_evaluation(method, specialTeachers)
      } catch (e) {
        console.error('[useApi] start_evaluation error:', e)
      }
    },
    [api]
  )

  const openGithub = useCallback(async (): Promise<void> => {
    if (!api) return
    try {
      await api.open_github()
    } catch (e) {
      console.error('[useApi] open_github error:', e)
    }
  }, [api])

  return { ready, error, login, getTaskInfo, startEvaluation, openGithub }
}
