import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,
})

// Add access token to requests

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('access_token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

let isRefreshing = false
let failedQueue = []
let refreshFailed = false

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })

  failedQueue = []
}
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Stop infinite loop for auth endpoints
    const isAuthRoute =
      originalRequest.url?.includes('/auth/refresh') ||
      originalRequest.url?.includes('/auth/session') ||
      originalRequest.url?.includes('/auth/google') ||
      originalRequest.url?.includes('/auth/logout')

    // If auth route itself failed, do not retry
    if (isAuthRoute) {
      return Promise.reject(error)
    }

    // Only retry once for non-auth routes
    if (error.response?.status === 401 && !originalRequest._retry) {

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const { data } = await axios.post(
          `${import.meta.env.VITE_API_URL}/auth/refresh`,
          {},
          { withCredentials: true }
        )

        const newAccessToken = data.access_token

        sessionStorage.setItem('access_token', newAccessToken)

        api.defaults.headers.common[
          'Authorization'
        ] = `Bearer ${newAccessToken}`

        processQueue(null, newAccessToken)

        originalRequest.headers.Authorization =
          `Bearer ${newAccessToken}`

        return api(originalRequest)

      } catch (refreshError) {

        processQueue(refreshError, null)

        sessionStorage.removeItem('access_token')

        return Promise.reject(refreshError)

      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api