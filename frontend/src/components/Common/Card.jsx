import React from 'react';

const Card = ({ title, value, subtitle, icon, color = 'primary', trend }) => {
  const colorClasses = {
    primary: 'bg-acidtech-primary',
    secondary: 'bg-acidtech-secondary',
    accent: 'bg-acidtech-accent',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    danger: 'bg-red-500'
  };

  return (
    <div className="card-acidtech">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">
            {title}
          </p>
          <p className="text-2xl font-bold text-acidtech-dark mt-2">
            {value}
          </p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className={`flex items-center mt-2 text-sm ${
              trend.direction === 'up' ? 'text-green-600' : 'text-red-600'
            }`}>
              <span className="mr-1">
                {trend.direction === 'up' ? '↗' : '↘'}
              </span>
              {trend.value}
            </div>
          )}
        </div>
        {icon && (
          <div className={`w-12 h-12 ${colorClasses[color]} rounded-lg flex items-center justify-center`}>
            <span className="text-white text-xl">{icon}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default Card;