import { GoogleLogin } from '@react-oauth/google'
import { useAuth } from '../hooks/useAuth'

export default function GoogleLoginButton() {
  const { login } = useAuth()

  return (
    <GoogleLogin
      onSuccess={async (credentialResponse) => {
        try {
          // credential = ID TOKEN (JWT)
          await login(credentialResponse.credential)
        } catch (err) {
          console.error(err)
        }
      }}
      onError={() => {
        alert('Google login failed')
      }}
    />
  )
}