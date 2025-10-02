// Google OAuth Configuration
export const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || "your-google-client-id.apps.googleusercontent.com";

export const googleOAuthConfig = {
  clientId: GOOGLE_CLIENT_ID,
  redirectUri: `${window.location.origin}/auth/callback`,
  scope: 'openid email profile',
  responseType: 'code',
  prompt: 'select_account'
};