import { useCallback, useEffect, useState } from 'react'
import type { PyWebViewAPI, LoginResult, TaskInfo, EvaluationMethod } from '@/types/api'

declare global {
  interface Window {
    __pywebviewApiReady?: boolean
    __onPywebviewReady?: (callback: () => void) => void
  }
}

/**
 * Hook to access the pywebview API
 *
 * Uses early event capture from index.html to handle race condition
 * where pywebviewready fires before React mounts
 */
export function useApi() {
  const [ready, setReady] = useState(false)
  const [api, setApi] = useState<PyWebViewAPI | null>(null)

  useEffect(() => {
    const handleReady = () => {
      if (window.pywebview?.api) {
        setApi(window.pywebview.api)
        setReady(true)
      }
    }

    // Check if already ready
    if (window.pywebview?.api) {
      handleReady()
      return
    }

    // Use early capture mechanism from index.html
    if (window.__onPywebviewReady) {
      window.__onPywebviewReady(handleReady)
    }

    // Also listen for event (belt and suspenders)
    window.addEventListener('pywebviewready', handleReady)
    return () => window.removeEventListener('pywebviewready', handleReady)
  }, [])

  const login = useCallback(
    async (username: string, password: string): Promise<LoginResult> => {
      if (!api) return { success: false, message: 'API not ready' }
      return api.login(username, password)
    },
    [api]
  )

  const getTaskInfo = useCallback(async (): Promise<TaskInfo> => {
    if (!api) return { success: false, message: 'API not ready' }
    return api.get_task_info()
  }, [api])

  const startEvaluation = useCallback(
    async (method: EvaluationMethod, specialTeachers: string[]): Promise<void> => {
      if (!api) return
      return api.start_evaluation(method, specialTeachers)
    },
    [api]
  )

  const openGithub = useCallback(async (): Promise<void> => {
    if (!api) return
    return api.open_github()
  }, [api])

  return { ready, login, getTaskInfo, startEvaluation, openGithub }
}
