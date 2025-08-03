import { PublicClientApplication } from '@azure/msal-browser';
import { msalConfig, loginRequest, tokenRequest } from '../config/authConfig';

// Initialize MSAL instance
export const msalInstance = new PublicClientApplication(msalConfig);

class AuthService {
  constructor() {
    this.msalInstance = msalInstance;
    this.currentUser = null;
  }

  // Initialize MSAL
  async initialize() {
    try {
      await this.msalInstance.initialize();
      console.log('MSAL initialized successfully');
      return true;
    } catch (error) {
      console.error('MSAL initialization failed:', error);
      return false;
    }
  }

  // Sign in with redirect
  async signInRedirect() {
    try {
      await this.msalInstance.loginRedirect(loginRequest);
    } catch (error) {
      console.error('Sign in redirect failed:', error);
      throw error;
    }
  }

  // Sign in with popup
  async signInPopup() {
    try {
      const response = await this.msalInstance.loginPopup(loginRequest);
      this.currentUser = response.account;
      return response;
    } catch (error) {
      console.error('Sign in popup failed:', error);
      throw error;
    }
  }

  // Sign out
  async signOut() {
    try {
      const account = this.getCurrentAccount();
      if (account) {
        await this.msalInstance.logoutRedirect({
          account: account,
          postLogoutRedirectUri: msalConfig.auth.postLogoutRedirectUri
        });
      }
    } catch (error) {
      console.error('Sign out failed:', error);
      throw error;
    }
  }

  // Get current account
  getCurrentAccount() {
    const accounts = this.msalInstance.getAllAccounts();
    if (accounts.length === 0) {
      return null;
    }
    return accounts[0];
  }

  // Check if user is authenticated
  isAuthenticated() {
    const account = this.getCurrentAccount();
    return account !== null;
  }

  // Get access token
  async getAccessToken() {
    try {
      const account = this.getCurrentAccount();
      if (!account) {
        throw new Error('No account found');
      }

      const tokenResponse = await this.msalInstance.acquireTokenSilent({
        ...tokenRequest,
        account: account
      });

      return tokenResponse.accessToken;
    } catch (error) {
      console.error('Token acquisition failed:', error);
      
      // If silent token acquisition fails, try with popup
      try {
        const tokenResponse = await this.msalInstance.acquireTokenPopup(tokenRequest);
        return tokenResponse.accessToken;
      } catch (popupError) {
        console.error('Popup token acquisition also failed:', popupError);
        throw popupError;
      }
    }
  }

  // Get user profile
  getUserProfile() {
    const account = this.getCurrentAccount();
    if (!account) {
      return null;
    }

    return {
      id: account.homeAccountId,
      name: account.name || account.username,
      email: account.username,
      roles: account.idTokenClaims?.roles || [],
      displayName: account.idTokenClaims?.name,
      firstName: account.idTokenClaims?.given_name,
      lastName: account.idTokenClaims?.family_name
    };
  }

  // Handle redirect result
  async handleRedirectPromise() {
    try {
      const response = await this.msalInstance.handleRedirectPromise();
      if (response && response.account) {
        this.currentUser = response.account;
        console.log('Redirect authentication successful');
        return response;
      }
      return null;
    } catch (error) {
      console.error('Handle redirect promise failed:', error);
      throw error;
    }
  }

  // Check for authentication state
  async checkAuthState() {
    try {
      await this.handleRedirectPromise();
      return this.isAuthenticated();
    } catch (error) {
      console.error('Check auth state failed:', error);
      return false;
    }
  }
}

// Create singleton instance
const authService = new AuthService();

export default authService;