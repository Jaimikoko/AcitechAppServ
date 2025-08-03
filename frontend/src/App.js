import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MsalProvider, AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react';
import { PublicClientApplication } from '@azure/msal-browser';
import { msalConfig } from './config/authConfig';
import AppLayout from './components/layout/AppLayout';
import ComingSoon from './pages/ComingSoon';
import Login from './components/Login/Login';
import './styles/index.css';

// Initialize MSAL instance
const msalInstance = new PublicClientApplication(msalConfig);

function App() {
  return (
    <MsalProvider instance={msalInstance}>
      <BrowserRouter>
        <div className="App">
          <AuthenticatedTemplate>
            <AppLayout>
              <Routes>
                {/* Dashboard Principal */}
                <Route path="/" element={<ComingSoon module="Dashboard" priority={3} />} />
                
                {/* PRIORIDAD 1: Cash Flow - CRÍTICO */}
                <Route path="/cashflow" element={<ComingSoon module="Cash Flow" priority={1} />} />
                
                {/* PRIORIDAD 2: Accounts - MUY IMPORTANTE */}
                <Route path="/accounts" element={<ComingSoon module="Accounts" priority={2} />} />
                
                {/* PRIORIDAD 3: Módulos importantes */}
                <Route path="/projections" element={<ComingSoon module="Projections" priority={3} />} />
                <Route path="/reports" element={<ComingSoon module="Reports" priority={3} />} />
                <Route path="/transactions" element={<ComingSoon module="Transactions" priority={3} />} />
                <Route path="/purchase-orders" element={<ComingSoon module="Purchase Orders" priority={3} />} />
                
                {/* FUTURO: Otros módulos */}
                <Route path="/payables" element={<ComingSoon module="Payables" />} />
                <Route path="/receivables" element={<ComingSoon module="Receivables" />} />
                <Route path="/upload" element={<ComingSoon module="Upload Data" />} />
                <Route path="/users" element={<ComingSoon module="Users" />} />
                <Route path="/logs" element={<ComingSoon module="System Logs" />} />
                <Route path="/settings" element={<ComingSoon module="Settings" />} />
              </Routes>
            </AppLayout>
          </AuthenticatedTemplate>
          
          <UnauthenticatedTemplate>
            <Login />
          </UnauthenticatedTemplate>
        </div>
      </BrowserRouter>
    </MsalProvider>
  );
}

export default App;