import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="loading-page">
        <div className="spinner" />
        <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: 13 }}>
          authenticating...
        </span>
      </div>
    )
  }

  return user ? <Outlet /> : <Navigate to="/login" replace />
}