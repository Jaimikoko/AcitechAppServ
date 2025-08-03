import React, { useState } from 'react';

const Navigation = ({ user, onLogout }) => {
  const [isOpen, setIsOpen] = useState(false);

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊', active: true },
    { id: 'transactions', label: 'Transactions', icon: '💳', active: false },
    { id: 'analytics', label: 'Analytics', icon: '📈', active: false },
    { id: 'reports', label: 'Reports', icon: '📋', active: false },
    { id: 'settings', label: 'Settings', icon: '⚙️', active: false }
  ];

  return (
    <div className={`bg-white shadow-lg h-screen transition-all duration-300 ${
      isOpen ? 'w-64' : 'w-16'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className={`flex items-center ${isOpen ? 'space-x-3' : 'justify-center'}`}>
          <div className="w-8 h-8 bg-gradient-to-br from-acidtech-primary to-acidtech-secondary rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">A</span>
          </div>
          {isOpen && (
            <span className="font-bold text-acidtech-dark">AcidTech</span>
          )}
        </div>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <span className="text-gray-500">{isOpen ? '←' : '→'}</span>
        </button>
      </div>

      {/* Menu Items */}
      <nav className="mt-6">
        <ul className="space-y-2 px-3">
          {menuItems.map((item) => (
            <li key={item.id}>
              <button
                className={`w-full flex items-center p-3 rounded-lg transition-all duration-200 ${
                  item.active
                    ? 'bg-acidtech-primary text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                } ${!isOpen ? 'justify-center' : 'space-x-3'}`}
              >
                <span className="text-lg">{item.icon}</span>
                {isOpen && (
                  <span className="font-medium">{item.label}</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* User Section */}
      {user && (
        <div className="absolute bottom-0 left-0 right-0 p-3 border-t border-gray-200">
          <div className={`flex items-center ${isOpen ? 'space-x-3' : 'justify-center'}`}>
            <div className="w-8 h-8 bg-acidtech-secondary rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">
                {user.name?.charAt(0).toUpperCase()}
              </span>
            </div>
            {isOpen && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-acidtech-dark truncate">
                  {user.name}
                </p>
                <button
                  onClick={onLogout}
                  className="text-xs text-gray-500 hover:text-acidtech-primary"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Navigation;