/**
 * Type definitions for the Python backend API
 */

export type EvaluationMethod = 'good' | 'random' | 'worst_passing'

export interface LoginResult {
  success: boolean
  message: string
}

export interface TaskInfo {
  success: boolean
  message?: string
  task_id?: string
  task_name?: string
}

export interface EvaluationProgress {
  current: number
  total: number
  course: string
  teacher: string
  special: boolean
}

export interface PyWebViewAPI {
  login: (username: string, password: string) => Promise<LoginResult>
  get_task_info: () => Promise<TaskInfo>
  start_evaluation: (method: EvaluationMethod, special_teachers: string[]) => Promise<void>
  open_github: () => Promise<void>
}

declare global {
  interface Window {
    pywebview: {
      api: PyWebViewAPI
    }
  }
}
