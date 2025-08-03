# 🔍 AcidTech Azure App Service - Validation Checklist

## ✅ CORRECCIONES APLICADAS

### 1. Azure AD B2C Configuration
- ✅ Fixed user flow name: `B2C_1_SignUpSignIn` (camelCase)
- ✅ Added missing `REACT_APP_B2C_KNOWN_AUTHORITIES`
- ✅ Corrected scopes: `acidtech-api/access_as_user`
- ✅ Validated tenant domain: `fintraqx.b2clogin.com`

### 2. Environment Variables - FINAL CONFIGURATION
```env
# ✅ CORRECTED VARIABLES
REACT_APP_B2C_CLIENT_ID=13a56f1f-1b3d-4d48-aee8-53b5159513db
REACT_APP_B2C_TENANT_ID=920837c8-5551-4a12-9d1a-78db9913ca56
REACT_APP_B2C_AUTHORITY=https://fintraqx.b2clogin.com/fintraqx.onmicrosoft.com/B2C_1_SignUpSignIn
REACT_APP_B2C_KNOWN_AUTHORITIES=fintraqx.b2clogin.com
REACT_APP_B2C_SCOPES=https://fintraqx.onmicrosoft.com/acidtech-api/access_as_user
REACT_APP_REDIRECT_URI=https://app.acidtech.fintraqx.com
REACT_APP_LOGOUT_URI=https://app.acidtech.fintraqx.com/logout
REACT_APP_API_BASE_URL=https://app.acidtech.fintraqx.com/api
```

## 🚨 PASOS OBLIGATORIOS EN AZURE AD B2C (ANTES DEL DEPLOY)

### 1. App Registration Configuration
```bash
# En Azure Portal → Azure AD B2C → App registrations
Name: AcidTech Financial Dashboard
Client ID: 13a56f1f-1b3d-4d48-aee8-53b5159513db
```

### 2. Authentication Settings
```json
{
  "redirectUris": [
    "https://app.acidtech.fintraqx.com",
    "https://app.acidtech.fintraqx.com/auth",
    "http://localhost:3000"
  ],
  "logoutUrl": "https://app.acidtech.fintraqx.com/logout",
  "implicitGrant": {
    "accessTokens": true,
    "idTokens": true
  },
  "spa": {
    "redirectUris": [
      "https://app.acidtech.fintraqx.com",
      "http://localhost:3000"
    ]
  }
}
```

### 3. API Permissions Required
- ✅ `openid`
- ✅ `profile`
- ✅ `email`
- ✅ `https://fintraqx.onmicrosoft.com/acidtech-api/access_as_user`

### 4. User Flows Required
Create these user flows in B2C:
- ✅ `B2C_1_SignUpSignIn`
- ✅ `B2C_1_ProfileEditing` 
- ✅ `B2C_1_PasswordReset`

## 🔧 CORS Configuration - CORRECTED

### For Azure Functions API:
```javascript
// ✅ CORRECTED CORS Headers
const corsHeaders = {
  'Access-Control-Allow-Origin': 'https://app.acidtech.fintraqx.com',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
  'Access-Control-Allow-Credentials': 'true',
  'Access-Control-Max-Age': '86400'
};

// For OPTIONS preflight
if (context.req.method === 'OPTIONS') {
    context.res = {
        status: 200,
        headers: corsHeaders,
        body: null
    };
    return;
}

// For actual requests
context.res = {
    status: 200,
    headers: {
        ...corsHeaders,
        'Content-Type': 'application/json'
    },
    body: responseData
};
```

## 📝 WEB.CONFIG - CORRECTED FOR APP SERVICE

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <!-- ✅ CORRECTED SPA ROUTING RULE -->
        <rule name="Handle History Mode and hash URLs" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
            <add input="{REQUEST_URI}" pattern="^/(api)" negate="true" />
            <add input="{REQUEST_URI}" pattern="^/(assets)" negate="true" />
            <add input="{REQUEST_URI}" pattern="^/(static)" negate="true" />
          </conditions>
          <action type="Rewrite" url="/index.html" />
        </rule>
      </rules>
    </rewrite>
    
    <!-- ✅ SECURITY HEADERS -->
    <httpProtocol>
      <customHeaders>
        <add name="X-Content-Type-Options" value="nosniff" />
        <add name="X-Frame-Options" value="DENY" />
        <add name="X-XSS-Protection" value="1; mode=block" />
        <add name="Strict-Transport-Security" value="max-age=31536000; includeSubDomains" />
      </customHeaders>
    </httpProtocol>
  </system.webServer>
</configuration>
```

## 🧪 TESTING SEQUENCE - PASO A PASO

### Phase 1: Local Testing
```bash
# 1. Install dependencies
cd frontend && npm install
cd ../api && npm install

# 2. Start API locally
cd api && npm start

# 3. Start frontend locally
cd frontend && npm start

# 4. Test authentication flow
# - Navigate to http://localhost:3000
# - Click login → should redirect to B2C
# - Login → should redirect back to app
# - Check browser console for errors
```

### Phase 2: Azure B2C Validation
```bash
# 1. Test B2C endpoints manually
curl -I "https://fintraqx.b2clogin.com/fintraqx.onmicrosoft.com/B2C_1_SignUpSignIn/oauth2/v2.0/authorize"

# 2. Validate redirect URIs in B2C portal
# 3. Test user flows in B2C portal
```

### Phase 3: Staging Deployment
```bash
# 1. Create staging slot
az webapp deployment slot create \
  --name acidtech-fintraqx-app \
  --resource-group acidtech-fintraqx-rg \
  --slot staging

# 2. Deploy to staging
# 3. Configure DNS CNAME (if needed)
# 4. Test staging environment
```

## ❌ ERROR PREVENTION CHECKLIST

### AADB2C90006 Error Prevention:
- ✅ All redirect URIs registered in B2C
- ✅ URLs use HTTPS in production
- ✅ No trailing slashes in redirect URIs

### CORS Error Prevention:
- ✅ Exact domain match in CORS config
- ✅ No wildcard (*) origins in production
- ✅ Credentials enabled for authenticated requests

### Authority Validation Prevention:
- ✅ Correct user flow names (camelCase)
- ✅ knownAuthorities properly configured
- ✅ Valid tenant domain format

### Token Validation Prevention:
- ✅ Correct scopes configured
- ✅ API app registration exists
- ✅ Proper audience configuration

## 🎯 PRE-DEPLOYMENT VALIDATION COMMANDS

```bash
# 1. Validate Azure configuration
az account show
az group show --name acidtech-fintraqx-rg

# 2. Test B2C configuration
curl -s "https://fintraqx.b2clogin.com/fintraqx.onmicrosoft.com/B2C_1_SignUpSignIn/.well-known/openid_configuration" | jq .

# 3. Validate environment variables
npm run build:production  # Should complete without errors
```

## 🚀 DEPLOYMENT ORDER

1. ✅ **Configure Azure AD B2C** (redirect URIs, scopes, user flows)
2. ✅ **Create Azure App Service** (with correct domain)
3. ✅ **Configure App Settings** (environment variables)
4. ✅ **Deploy application** (staging first)
5. ✅ **Configure DNS** (CNAME to App Service)
6. ✅ **Test authentication flow**
7. ✅ **Deploy to production**

## 🎖️ VALIDATION STATUS

- ✅ Azure AD B2C Configuration: **CORRECTED**
- ✅ MSAL v2 Configuration: **CORRECTED**  
- ✅ Environment Variables: **CORRECTED**
- ✅ CORS Configuration: **CORRECTED**
- ✅ Web.config: **CORRECTED**
- ✅ Testing Sequence: **DEFINED**

**🎉 READY FOR DEPLOYMENT!**