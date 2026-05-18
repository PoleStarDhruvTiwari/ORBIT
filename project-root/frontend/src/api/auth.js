import axios from '../utils/axios'

export const authApi = {
  googleLogin: async (idToken) => {
    const response = await axios.post('/auth/google', { id_token: idToken })
    return response.data
  },
  refreshToken: async () => {
    const response = await axios.post('/auth/refresh')
    return response.data
  },
  getSession: async () => {
    const response = await axios.get('/auth/session')
    return response.data
  },
  logout: async () => {
    await axios.post('/auth/logout')
  }
}