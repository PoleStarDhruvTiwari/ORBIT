import { AuthProvider } from './context/AuthContext'
import { useAuth } from './hooks/useAuth'
import GoogleLoginButton from './components/GoogleLoginButton'

function Dashboard() {
  const { user, accessToken, refreshToken, logout, refreshAccessToken } = useAuth()

  return (
    <div style={{ padding: '20px' }}>
      <h1>Shift Management - Auth Test</h1>
      {user ? (
        <div>
          <p>Welcome, {user.name} ({user.email})</p>
          <p>Role: {user.role}</p>
          <div style={{ background: '#f0f0f0', padding: '10px', margin: '10px 0' }}>
            <strong>Access Token:</strong>
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{accessToken}</pre>
            <strong>Refresh Token (from login response):</strong>
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{refreshToken}</pre>
          </div>
          <button onClick={refreshAccessToken}>Refresh Access Token</button>
          <button onClick={logout} style={{ marginLeft: '10px' }}>Logout</button>
        </div>
      ) : (
        <div>
          <p>Please log in with Google.</p>
          <GoogleLoginButton />
        </div>
      )}
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <Dashboard />
    </AuthProvider>
  )
}

export default App