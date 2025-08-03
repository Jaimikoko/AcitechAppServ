import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const menuSections = [
    {
      id: 'overview',
      title: 'OVERVIEW',
      items: [
        { id: 'dashboard', icon: '📊', label: 'Dashboard', path: '/', priority: 3 },
        { id: 'cashflow', icon: '🔥', label: 'Cash Flow', path: '/cashflow', priority: 1 }
      ]
    },
    {
      id: 'analytics',
      title: 'ANALYTICS',
      items: [
        { id: 'projections', icon: '📈', label: 'Projections', path: '/projections', priority: 3 },
        { id: 'reports', icon: '📋', label: 'Reports', path: '/reports', priority: 3 }
      ]
    },
    {
      id: 'manage',
      title: 'MANAGE',
      items: [
        { id: 'accounts', icon: '🏦', label: 'Accounts', path: '/accounts', priority: 2 },
        { id: 'transactions', icon: '💳', label: 'Transactions', path: '/transactions', priority: 3 },
        { id: 'payables', icon: '💰', label: 'Payables', path: '/payables' },
        { id: 'receivables', icon: '💼', label: 'Receivables', path: '/receivables' },
        { id: 'purchase-orders', icon: '🛒', label: 'Purchase Orders', path: '/purchase-orders', priority: 3 }
      ]
    },
    {
      id: 'admin',
      title: 'ADMIN TOOLS',
      items: [
        { id: 'upload', icon: '📤', label: 'Upload Data', path: '/upload' },
        { id: 'users', icon: '👥', label: 'Users', path: '/users' },
        { id: 'logs', icon: '📝', label: 'System Logs', path: '/logs' },
        { id: 'settings', icon: '⚙️', label: 'Settings', path: '/settings' }
      ]
    }
  ];

  const getPriorityIndicator = (priority) => {
    switch(priority) {
      case 1: return <span className="ml-2 text-xs bg-red-500 text-white px-1 rounded">🔥</span>;
      case 2: return <span className="ml-2 text-xs bg-orange-500 text-white px-1 rounded">⚡</span>;
      case 3: return <span className="ml-2 text-xs bg-blue-500 text-white px-1 rounded">📋</span>;
      default: return null;
    }
  };

  return (
    <div className={`bg-slate-800 text-white transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64'}`}>
      {/* Header */}
      <div className="p-4 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <div className={`flex items-center space-x-3 ${isCollapsed ? 'justify-center' : ''}`}>
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">A</span>
            </div>
            {!isCollapsed && (
              <div>
                <h1 className="font-bold text-lg">AcidTech</h1>
                <p className="text-xs text-slate-400">Financial Dashboard</p>
              </div>
            )}
          </div>
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 rounded hover:bg-slate-700"
          >
            <span className="text-slate-400">☰</span>
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-6">
        {menuSections.map(section => (
          <div key={section.id}>
            {!isCollapsed && (
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">
                {section.title}
              </h3>
            )}
            <div className="space-y-1">
              {section.items.map(item => (
                <button
                  key={item.id}
                  onClick={() => navigate(item.path)}
                  className={`
                    w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors text-left
                    ${location.pathname === item.path 
                      ? 'bg-blue-600 text-white' 
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                    }
                    ${isCollapsed ? 'justify-center px-2' : ''}
                  `}
                >
                  <span className="text-xl">{item.icon}</span>
                  {!isCollapsed && (
                    <>
                      <span className="flex-1">{item.label}</span>
                      {getPriorityIndicator(item.priority)}
                    </>
                  )}
                </button>
              ))}
            </div>
          </div>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;