/**
 * Azure AD B2C Configuration for AcidTech Financial Dashboard
 * Tenant: hello@fintraqx.com (Fintraqx B2C)
 * Domain: app.acidtech.fintraqx.com
 */

// B2C Configuration for Fintraqx tenant
const b2cConfig = {
    // App Registration Details
    clientId: process.env.REACT_APP_CLIENT_ID || "13a56f1f-1b3d-4d48-aee8-53b5159513db",
    
    // Tenant Configuration - NEW TENANT
    tenantName: "fintraqx",
    tenantId: process.env.REACT_APP_TENANT_ID || "920837c8-5551-4a12-9d1a-78db9913ca56",
    
    // B2C Authority and Endpoints
    authority: process.env.REACT_APP_AUTHORITY || "https://fintraqx.b2clogin.com/fintraqx.onmicrosoft.com/B2C_1_SignUpSignIn",
    knownAuthorities: [process.env.REACT_APP_B2C_KNOWN_AUTHORITIES || "fintraqx.b2clogin.com"],
    
    // Redirect URLs - Azure App Service Domain
    redirectUri: process.env.REACT_APP_REDIRECT_URI || "https://acidtech-prod-app.azurewebsites.net",
    postLogoutRedirectUri: process.env.REACT_APP_LOGOUT_URI || "https://acidtech-prod-app.azurewebsites.net/logout",
    
    // User Flows (Policies)
    policies: {
        signUpSignIn: "B2C_1_SignUpSignIn",
        profileEdit: "B2C_1_ProfileEditing",
        passwordReset: "B2C_1_PasswordReset"
    },
    
    // API Scopes - NEW TENANT SCOPE
    scopes: [
        "openid",
        "profile", 
        "email",
        process.env.REACT_APP_SCOPES || "api://acidtech-api/access_as_user"
    ],
    
    // Cache Configuration
    cache: {
        cacheLocation: "localStorage",
        storeAuthStateInCookie: true // For IE11 and Edge compatibility
    }
};

// Environment-specific configuration
const environmentConfig = {
    production: {
        ...b2cConfig,
        redirectUri: "https://acidtech-prod-app.azurewebsites.net",
        postLogoutRedirectUri: "https://acidtech-prod-app.azurewebsites.net/logout"
    },
    development: {
        ...b2cConfig,
        redirectUri: "http://localhost:3000",
        postLogoutRedirectUri: "http://localhost:3000"
    }
};

// Get current environment
function getCurrentEnvironment() {
    return process.env.NODE_ENV === 'production' ? 'production' : 'development';
}

// Current configuration based on environment
const currentConfig = environmentConfig[getCurrentEnvironment()];

// MSAL Configuration for v2 with PKCE
export const msalConfig = {
    auth: {
        clientId: currentConfig.clientId,
        authority: currentConfig.authority,
        knownAuthorities: currentConfig.knownAuthorities,
        redirectUri: currentConfig.redirectUri,
        postLogoutRedirectUri: currentConfig.postLogoutRedirectUri,
        navigateToLoginRequestUrl: false
    },
    cache: currentConfig.cache,
    system: {
        loggerOptions: {
            loggerCallback: (level, message, containsPii) => {
                if (containsPii) return;
                
                switch (level) {
                    case 0: // Error  
                        console.error('MSAL Error:', message);
                        break;
                    case 1: // Warning
                        console.warn('MSAL Warning:', message);
                        break;
                    case 2: // Info
                        console.info('MSAL Info:', message);
                        break;
                    case 3: // Verbose
                        console.log('MSAL Verbose:', message);
                        break;
                }
            },
            piiLoggingEnabled: false,
            logLevel: process.env.NODE_ENV === 'production' ? 1 : 2
        },
        allowNativeBroker: false // Disable for web apps
    }
};

// Login Request Configuration
export const loginRequest = {
    scopes: currentConfig.scopes,
    prompt: "select_account"
};

// Token Request Configuration  
export const tokenRequest = {
    scopes: currentConfig.scopes,
    forceRefresh: false
};

// Profile Edit Request
export const profileEditRequest = {
    authority: `https://${currentConfig.tenantName}.b2clogin.com/${currentConfig.tenantName}.onmicrosoft.com/${currentConfig.policies.profileEdit}`,
    scopes: currentConfig.scopes
};

// Password Reset Request
export const passwordResetRequest = {
    authority: `https://${currentConfig.tenantName}.b2clogin.com/${currentConfig.tenantName}.onmicrosoft.com/${currentConfig.policies.passwordReset}`,
    scopes: currentConfig.scopes
};

// User Claims Configuration
export const userClaims = {
    displayName: "name",
    email: "emails[0]",
    firstName: "given_name", 
    lastName: "family_name",
    objectId: "oid",
    userRole: "extension_UserRole"
};

// User Roles
export const userRoles = {
    ADMIN: "admin",
    USER: "user",
    READONLY: "readonly", 
    ACCOUNTANT: "accountant",
    MANAGER: "manager"
};

// Configuration validation
export function validateB2CConfig() {
    const requiredFields = ['clientId', 'authority', 'redirectUri'];
    const missingFields = requiredFields.filter(field => 
        !currentConfig[field] || currentConfig[field].includes('YOUR_')
    );
    
    if (missingFields.length > 0) {
        console.error('B2C Configuration incomplete:', missingFields);
        return false;
    }
    
    return true;
}

// Export current configuration
export { currentConfig };

// Log configuration status
if (typeof window !== 'undefined') {
    const isValid = validateB2CConfig();
    console.log(`B2C Configuration: ${isValid ? 'Valid' : 'Invalid'}`);
    console.log(`Environment: ${getCurrentEnvironment()}`);
    console.log(`Domain: ${currentConfig.redirectUri}`);
}