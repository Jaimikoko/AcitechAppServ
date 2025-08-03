import React, { useState, useEffect } from 'react';
import Header from '../Common/Header';
import Card from '../Common/Card';
import Navigation from '../Navigation/Navigation';

const Dashboard = ({ user, onLogout }) => {
  const [dashboardData, setDashboardData] = useState({
    totalBalance: '$24,580.00',
    monthlyIncome: '$8,240.00',
    monthlyExpenses: '$3,680.00',
    savings: '$4,560.00',
    recentTransactions: [
      { id: 1, description: 'Salary Payment', amount: '+$3,500.00', date: '2024-01-15', type: 'income' },
      { id: 2, description: 'Grocery Store', amount: '-$127.50', date: '2024-01-14', type: 'expense' },
      { id: 3, description: 'Electric Bill', amount: '-$89.20', date: '2024-01-13', type: 'expense' },
      { id: 4, description: 'Freelance Project', amount: '+$750.00', date: '2024-01-12', type: 'income' },
    ]
  });

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading data
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-acidtech-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar Navigation */}
      <Navigation user={user} onLogout={onLogout} />

      {/* Main Content */}
      <div className="flex-1">
        <Header 
          title="Dashboard" 
          subtitle="Welcome back! Here's your financial overview."
          user={user}
        />

        <main className="p-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card
              title="Total Balance"
              value={dashboardData.totalBalance}
              subtitle="All accounts"
              icon="💰"
              color="primary"
              trend={{ direction: 'up', value: '+12.5%' }}
            />
            <Card
              title="Monthly Income"
              value={dashboardData.monthlyIncome}
              subtitle="This month"
              icon="📈"
              color="success"
              trend={{ direction: 'up', value: '+8.2%' }}
            />
            <Card
              title="Monthly Expenses"
              value={dashboardData.monthlyExpenses}
              subtitle="This month"
              icon="📉"
              color="warning"
              trend={{ direction: 'down', value: '-3.1%' }}
            />
            <Card
              title="Savings"
              value={dashboardData.savings}
              subtitle="Available"
              icon="🏦"
              color="secondary"
              trend={{ direction: 'up', value: '+15.7%' }}
            />
          </div>

          {/* Charts and Recent Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Spending Chart Placeholder */}
            <div className="card-acidtech">
              <h3 className="text-lg font-semibold text-acidtech-dark mb-4">
                Monthly Spending Overview
              </h3>
              <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <div className="text-4xl mb-2">📊</div>
                  <p>Chart will be displayed here</p>
                  <p className="text-sm">Connect your financial data</p>
                </div>
              </div>
            </div>

            {/* Recent Transactions */}
            <div className="card-acidtech">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-acidtech-dark">
                  Recent Transactions
                </h3>
                <button className="text-acidtech-primary hover:text-acidtech-secondary text-sm font-medium">
                  View All
                </button>
              </div>
              <div className="space-y-3">
                {dashboardData.recentTransactions.map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        transaction.type === 'income' ? 'bg-green-100' : 'bg-red-100'
                      }`}>
                        <span className="text-lg">
                          {transaction.type === 'income' ? '↗️' : '↘️'}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-acidtech-dark">
                          {transaction.description}
                        </p>
                        <p className="text-sm text-gray-500">
                          {transaction.date}
                        </p>
                      </div>
                    </div>
                    <div className={`font-semibold ${
                      transaction.type === 'income' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {transaction.amount}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Action Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="card-acidtech text-center">
              <div className="text-4xl mb-3">📱</div>
              <h4 className="font-semibold text-acidtech-dark mb-2">
                Connect Bank Account
              </h4>
              <p className="text-gray-600 text-sm mb-4">
                Link your bank account for automatic transaction tracking
              </p>
              <button className="btn-acidtech w-full">
                Connect Account
              </button>
            </div>

            <div className="card-acidtech text-center">
              <div className="text-4xl mb-3">📸</div>
              <h4 className="font-semibold text-acidtech-dark mb-2">
                Scan Receipt
              </h4>
              <p className="text-gray-600 text-sm mb-4">
                Use AI to extract data from receipts and invoices
              </p>
              <button className="btn-acidtech w-full">
                Scan Now
              </button>
            </div>

            <div className="card-acidtech text-center">
              <div className="text-4xl mb-3">📋</div>
              <h4 className="font-semibold text-acidtech-dark mb-2">
                Generate Report
              </h4>
              <p className="text-gray-600 text-sm mb-4">
                Create detailed financial reports and insights
              </p>
              <button className="btn-acidtech w-full">
                Create Report
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;