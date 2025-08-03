import React, { useState } from 'react';

const Login = ({ onLogin, isLoading }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onLogin) {
      onLogin({ email, password });
    }
  };

  const handleAzureLogin = () => {
    if (onLogin) {
      onLogin({ provider: 'azure' });
    }
  };

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo Section */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full shadow-lg mb-4">
            <span className="text-2xl font-bold bg-gradient-to-r from-acidtech-primary to-acidtech-secondary bg-clip-text text-transparent">
              A
            </span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">
            AcidTech Financial
          </h1>
          <p className="text-white/80">
            Your intelligent financial dashboard
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-acidtech-dark mb-6 text-center">
            Welcome Back
          </h2>

          {/* Azure AD B2C Login Button */}
          <button
            onClick={handleAzureLogin}
            disabled={isLoading}
            className="w-full bg-white border-2 border-gray-200 text-acidtech-dark font-medium py-3 px-4 rounded-lg hover:border-acidtech-primary hover:bg-acidtech-light transition-all duration-200 flex items-center justify-center space-x-2 mb-6"
          >
            <span className="text-xl">🔐</span>
            <span>Continue with Azure AD</span>
          </button>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or continue with email</span>
            </div>
          </div>

          {/* Email/Password Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-acidtech"
                placeholder="Enter your email"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-acidtech"
                placeholder="Enter your password"
                required
              />
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center">
                <input type="checkbox" className="mr-2 text-acidtech-primary" />
                <span className="text-gray-600">Remember me</span>
              </label>
              <a href="#" className="text-acidtech-primary hover:text-acidtech-secondary">
                Forgot password?
              </a>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={`w-full btn-acidtech py-3 ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <a href="#" className="text-acidtech-primary hover:text-acidtech-secondary font-medium">
              Sign up here
            </a>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-white/60 text-sm">
          <p>© 2024 AcidTech Financial. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default Login;