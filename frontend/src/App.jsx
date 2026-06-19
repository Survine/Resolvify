import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import CustomerChat from './pages/CustomerChat.jsx'

export default function App() {
  const { token } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={token ? <Navigate to="/dashboard" /> : <Login />} />
      <Route path="/dashboard" element={token ? <Dashboard /> : <Navigate to="/login" />} />
      <Route path="/chat" element={<CustomerChat />} />
      <Route path="*" element={<Navigate to={token ? '/dashboard' : '/chat'} />} />
    </Routes>
  )
}
