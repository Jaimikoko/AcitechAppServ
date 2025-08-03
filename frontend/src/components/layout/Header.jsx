import { useMsal } from '@azure/msal-react';
import { useState, useEffect } from 'react';

const Header = () => {
  const { accounts } = useMsal();
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentDate(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);
  
  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold text-gray-800">AcidTech Financial Dashboard</h2>
        </div>
        
        <div className="flex items-center space-x-6">
          {/* Status Indicators */}
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
              <span className="text-gray-600">APIs: Using Mocks</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
              <span className="text-gray-600">Shell Mode</span>
            </div>
          </div>
          
          {/* Date and Time */}
          <div className="text-right text-sm">
            <div className="text-gray-800 font-medium">{formatDate(currentDate)}</div>
            <div className="text-gray-500">Last updated: {formatTime(currentDate)}</div>
          </div>
          
          {/* User Info */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">
                {accounts[0]?.name?.charAt(0) || 'U'}
              </span>
            </div>
            <span className="text-sm text-gray-600">
              {accounts[0]?.name || 'User'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;