import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'

export const TOKEN_KEY = 'gym_auth_token'

interface AuthState {
  token: string | null
  username: string | null
  isTemporary: boolean
}

interface AuthContextValue extends AuthState {
  login: (token: string, username: string, isTemporary: boolean) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

function parseToken(token: string): { username: string; isTemporary: boolean; exp: number } | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return { username: payload.sub, isTemporary: payload.is_temporary ?? false, exp: payload.exp }
  } catch {
    return null
  }
}

function loadInitialState(): AuthState {
  const token = localStorage.getItem(TOKEN_KEY)
  if (!token) return { token: null, username: null, isTemporary: false }
  const parsed = parseToken(token)
  if (!parsed || Date.now() / 1000 > parsed.exp) {
    localStorage.removeItem(TOKEN_KEY)
    return { token: null, username: null, isTemporary: false }
  }
  return { token, username: parsed.username, isTemporary: parsed.isTemporary }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(loadInitialState)

  const login = useCallback((token: string, username: string, isTemporary: boolean) => {
    localStorage.setItem(TOKEN_KEY, token)
    setState({ token, username, isTemporary })
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setState({ token: null, username: null, isTemporary: false })
  }, [])

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
