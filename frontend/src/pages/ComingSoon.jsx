import { useNavigate } from 'react-router-dom';

const ComingSoon = ({ module, priority }) => {
  const navigate = useNavigate();
  
  const getPriorityBadge = (priority) => {
    switch(priority) {
      case 1: return (
        <div className="mb-4">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
            🔥 NEXT PRIORITY - Critical Module
          </span>
        </div>
      );
      case 2: return (
        <div className="mb-4">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800">
            ⚡ HIGH PRIORITY - Important Module
          </span>
        </div>
      );
      case 3: return (
        <div className="mb-4">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
            📋 PLANNED - Upcoming Module
          </span>
        </div>
      );
      default: return (
        <div className="mb-4">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
            📅 FUTURE - Planned Module
          </span>
        </div>
      );
    }
  };

  const getDescription = (priority) => {
    switch(priority) {
      case 1: return "This critical module is next in the development queue and will be implemented immediately.";
      case 2: return "This important module will be developed right after the critical modules are completed.";
      case 3: return "This module is planned for upcoming releases in the current development cycle.";
      default: return "This module will be implemented in future development phases.";
    }
  };

  const getIcon = (priority) => {
    switch(priority) {
      case 1: return "🔥";
      case 2: return "⚡";
      case 3: return "📋";
      default: return "🚧";
    }
  };
  
  return (
    <div className="flex items-center justify-center min-h-full coming-soon-container">
      <div className="text-center p-8 bg-white rounded-xl shadow-lg max-w-md w-full">
        {getPriorityBadge(priority)}
        
        <div className="text-6xl mb-4">{getIcon(priority)}</div>
        
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{module}</h1>
        <p className="text-lg text-gray-600 mb-4">Coming Soon</p>
        
        <p className="text-gray-500 mb-6 leading-relaxed">
          {getDescription(priority)}
        </p>

        {priority === 1 && (
          <div className="mb-6 p-4 bg-red-50 rounded-lg border border-red-200">
            <p className="text-red-800 text-sm font-medium">
              🚨 This is the next module to be developed. Implementation starts immediately.
            </p>
          </div>
        )}

        {priority === 2 && (
          <div className="mb-6 p-4 bg-orange-50 rounded-lg border border-orange-200">
            <p className="text-orange-800 text-sm font-medium">
              ⏰ High priority module - scheduled right after critical modules.
            </p>
          </div>
        )}
        
        <div className="space-y-3">
          <button 
            onClick={() => navigate(-1)}
            className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-200"
          >
            ← Go Back
          </button>
          
          <button 
            onClick={() => navigate('/')}
            className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors duration-200"
          >
            🏠 Dashboard Home
          </button>
        </div>

        <div className="mt-6 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-400">
            AcidTech Financial Dashboard v2.0 - Shell Mode
          </p>
        </div>
      </div>
    </div>
  );
};

export default ComingSoon;