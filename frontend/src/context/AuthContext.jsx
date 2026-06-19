import { createContext, useState, useEffect } from 'react'
import api from '../api/client'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [employee, setEmployee] = useState(null)
  const [loading, setLoading] = useState(!!token)

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token)
      api.get('/employees/me')
        .then((res) => setEmployee(res.data))
        .catch(() => { setToken(null); setEmployee(null) })
        .finally(() => setLoading(false))
    } else {
      localStorage.removeItem('token')
      setEmployee(null)
      setLoading(false)
    }
  }, [token])

  const login = async (username, password) => {
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)

    const { data } = await api.post('/auth/token', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    setToken(data.access_token)
  }

  const logout = () => {
    setToken(null)
    setEmployee(null)
  }

  return (
    <AuthContext.Provider value={{ token, employee, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
