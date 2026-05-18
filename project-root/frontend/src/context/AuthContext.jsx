import React, { createContext, useState, useEffect } from 'react'
import { authApi } from '../api/auth'

export const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [accessToken, setAccessToken] = useState(null)
  const [refreshToken, setRefreshToken] = useState(null)
  const [loading, setLoading] = useState(true)

  // Auto-login on app start
  useEffect(() => {
    const checkSession = async () => {
      try {
        const data = await authApi.getSession()
        setAccessToken(data.access_token)
        sessionStorage.setItem('access_token', data.access_token)
        setUser(data.user)
        setRefreshToken(null) // refresh token is in cookie, not stored in state
      } catch (err) {
        
        console.log('No active session')

        setUser(null)
        setAccessToken(null)
        setRefreshToken(null)

        sessionStorage.removeItem('access_token')


        setUser(null)
        setAccessToken(null)
        sessionStorage.removeItem('access_token')
      } finally {
        setLoading(false)
      }
    }
    checkSession()
  }, [])

  const login = async (idToken) => {
    try {
      const data = await authApi.googleLogin(idToken)
      setAccessToken(data.access_token)
      setRefreshToken(data.refresh_token)
      sessionStorage.setItem('access_token', data.access_token)
      // Fetch user info from /users/me or use data.user if backend returns it
      const userRes = await authApi.getSession()
      setUser(userRes.user)
    } catch (err) {
      if (err.response?.status === 403 && err.response?.data?.detail === 'user_not_registered') {
        alert('User not found in system. Please reach out to your lead to get access.')
      } else {
        alert('Login failed')
      }
      throw err
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      setUser(null)
      setAccessToken(null)
      setRefreshToken(null)
      sessionStorage.removeItem('access_token')
    }
  }

  const refreshAccessToken = async () => {
    try {
      const data = await authApi.refreshToken()
      setAccessToken(data.access_token)
      sessionStorage.setItem('access_token', data.access_token)
      alert('Access token refreshed')
    } catch (err) {
      console.error('Refresh failed', err)
      logout()
    }
  }

  return (
    <AuthContext.Provider value={{ user, accessToken, refreshToken, login, logout, refreshAccessToken, loading }}>
      {children}
    </AuthContext.Provider>
  )
}