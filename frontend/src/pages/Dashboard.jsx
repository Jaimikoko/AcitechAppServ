import React, { useState, useEffect } from 'react';
import apiService from '../services/apiService';

const Dashboard = () => {
  const [healthStatus, setHealthStatus] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Test Flask health endpoint
      const health = await apiService.checkHealth();
      setHealthStatus(health);

      // Load dashboard data
      const data = await apiService.getDashboardData();
      setDashboardData(data);

    } catch (err) {
      console.error('Dashboard load error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const MetricCard = ({ title, value, icon, color = "blue" }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`w-12 h-12 bg-${color}-100 rounded-lg flex items-center justify-center`}>
          <span className="text-2xl">{icon}</span>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center min-h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading dashboard data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <span className="text-red-500 text-2xl mr-3">⚠️</span>
            <div>
              <h3 className="text-red-800 font-semibold mb-2">Connection Error</h3>
              <p className="text-red-700">{error}</p>
              <button 
                onClick={loadDashboardData}
                className="mt-3 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
              >
                Retry Connection
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">AcidTech Financial Overview</p>
        </div>
        <button 
          onClick={loadDashboardData}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <span>🔄</span>
          <span>Refresh</span>
        </button>
      </div>

      {/* Flask Integration Status */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center">
          <span className="text-green-500 text-2xl mr-3">✅</span>
          <div>
            <h3 className="text-green-800 font-semibold">Flask Backend Connected</h3>
            <p className="text-green-700">
              Successfully connected to Flask API at {apiService.baseURL}
            </p>
            {healthStatus && (
              <p className="text-sm text-green-600 mt-1">
                API Status: {healthStatus.status} | Timestamp: {healthStatus.timestamp}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard 
          title="Total Transactions"
          value={dashboardData?.transactions?.summary?.transaction_count?.total || "0"}
          icon="💳"
          color="blue"
        />
        <MetricCard 
          title="Net Income"
          value={`$${dashboardData?.transactions?.summary?.net_income?.toLocaleString() || "0"}`}
          icon="💰"
          color="green"
        />
        <MetricCard 
          title="Purchase Orders"
          value={dashboardData?.purchaseOrders?.total || "0"}
          icon="🛒"
          color="purple"
        />
        <MetricCard 
          title="System Health"
          value="Operational"
          icon="⚡"
          color="yellow"
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center space-x-3 p-4 bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
            <span className="text-2xl">🔥</span>
            <div className="text-left">
              <p className="font-medium text-red-800">Cash Flow</p>
              <p className="text-sm text-red-600">Priority 1 - Next Implementation</p>
            </div>
          </button>
          <button className="flex items-center space-x-3 p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors">
            <span className="text-2xl">⚡</span>
            <div className="text-left">
              <p className="font-medium text-orange-800">Accounts</p>
              <p className="text-sm text-orange-600">Priority 2 - High Priority</p>
            </div>
          </button>
          <button className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
            <span className="text-2xl">📋</span>
            <div className="text-left">
              <p className="font-medium text-blue-800">Reports</p>
              <p className="text-sm text-blue-600">Priority 3 - Planned</p>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Activity (Mock Data) */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-xl">💳</span>
            <div className="flex-1">
              <p className="font-medium text-gray-900">New Transaction</p>
              <p className="text-sm text-gray-600">Client Payment - Invoice #INV-2024-001</p>
            </div>
            <span className="text-sm text-gray-500">5 min ago</span>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-xl">🛒</span>
            <div className="flex-1">
              <p className="font-medium text-gray-900">Purchase Order Created</p>
              <p className="text-sm text-gray-600">Office Supplies - $127.50</p>
            </div>
            <span className="text-sm text-gray-500">15 min ago</span>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-xl">📊</span>
            <div className="flex-1">
              <p className="font-medium text-gray-900">Flask API Connected</p>
              <p className="text-sm text-gray-600">Backend migration completed successfully</p>
            </div>
            <span className="text-sm text-gray-500">1 hour ago</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;