import React, { useState, useEffect, useCallback } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Platform icons mapping
const platformIcons = {
  Twitter: "🐦",
  Facebook: "📘", 
  Instagram: "📷"
};

// Threat level colors
const threatColors = {
  low: "bg-green-100 border-green-500 text-green-800",
  medium: "bg-yellow-100 border-yellow-500 text-yellow-800", 
  high: "bg-orange-100 border-orange-500 text-orange-800",
  critical: "bg-red-100 border-red-500 text-red-800"
};

const NotificationPopup = ({ notification, onClose }) => {
  if (!notification) return null;

  const bgColor = notification.type === 'success' 
    ? 'bg-green-50 border-green-200' 
    : 'bg-red-50 border-red-200';
    
  const textColor = notification.type === 'success'
    ? 'text-green-800'
    : 'text-red-800';

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm">
      <div className={`${bgColor} border rounded-lg shadow-lg p-4 ${textColor} animate-slide-in`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="font-semibold text-sm mb-1">{notification.title}</div>
            <div className="text-sm mb-1">{notification.message}</div>
            {notification.details && (
              <div className="text-xs opacity-75">{notification.details}</div>
            )}
          </div>
          <button
            onClick={onClose}
            className="ml-3 text-lg leading-none hover:opacity-75"
          >
            ×
          </button>
        </div>
      </div>
    </div>
  );
};

const ThreatAlert = ({ alert }) => {
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className={`border-l-4 p-4 mb-4 rounded-lg shadow-md ${threatColors[alert.threat_level]}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-2xl">{platformIcons[alert.platform]}</span>
          <span className="font-semibold text-lg">{alert.platform}</span>
          <span className={`px-2 py-1 rounded text-xs font-semibold uppercase ${threatColors[alert.threat_level]}`}>
            {alert.threat_level}
          </span>
        </div>
        <div className="text-sm text-gray-600">
          Score: {(alert.score * 100).toFixed(1)}%
        </div>
      </div>
      
      <div className="mb-3">
        <div className="font-medium text-gray-900">@{alert.author}</div>
        <div className="text-gray-700 mt-1 italic">"{alert.content}"</div>
      </div>
      
      <div className="mb-3">
        <div className="text-sm font-semibold text-gray-800">Detected Issues:</div>
        <div className="text-sm text-gray-600">{alert.reason}</div>
      </div>
      
      {alert.ai_analysis && (
        <div className="mb-3">
          <div className="text-sm font-semibold text-gray-800">AI Analysis:</div>
          <div className="text-sm text-gray-600">{alert.ai_analysis}</div>
        </div>
      )}
      
      <div className="flex justify-between items-center text-xs text-gray-500">
        <div>{formatTime(alert.timestamp)}</div>
        <a 
          href={alert.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline"
        >
          View Original Post →
        </a>
      </div>
    </div>
  );
};

const MonitoringStatus = ({ status, onStart, onStop, onClear }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">Monitoring Status</h2>
        <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
          status.is_running 
            ? 'bg-green-100 text-green-800' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          {status.is_running ? '🟢 ACTIVE' : '⭕ STOPPED'}
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{status.alerts_count}</div>
          <div className="text-sm text-gray-600">Total Alerts</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{status.platforms_monitored?.length || 0}</div>
          <div className="text-sm text-gray-600">Platforms</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">
            {status.last_check ? new Date(status.last_check).toLocaleTimeString() : '--:--'}
          </div>
          <div className="text-sm text-gray-600">Last Check</div>
        </div>
      </div>
      
      <div className="flex space-x-3">
        <button
          onClick={onStart}
          disabled={status.is_running}
          className={`px-4 py-2 rounded-md font-semibold ${
            status.is_running
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-green-600 text-white hover:bg-green-700'
          }`}
        >
          🟢 Start Monitoring
        </button>
        
        <button
          onClick={onStop}
          disabled={!status.is_running}
          className={`px-4 py-2 rounded-md font-semibold ${
            !status.is_running
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-red-600 text-white hover:bg-red-700'
          }`}
        >
          🔴 Stop Monitoring
        </button>
        
        <button
          onClick={onClear}
          className="px-4 py-2 bg-yellow-600 text-white rounded-md font-semibold hover:bg-yellow-700"
        >
          🗑️ Clear Alerts
        </button>
      </div>
    </div>
  );
};

function App() {
  const [alerts, setAlerts] = useState([]);
  const [status, setStatus] = useState({
    is_running: false,
    platforms_monitored: [],
    alerts_count: 0,
    last_check: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState(null);

  // Fetch alerts from API
  const fetchAlerts = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/alerts`);
      setAlerts(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching alerts:', err);
      setError('Failed to fetch alerts');
    }
  }, []);

  // Fetch monitoring status
  const fetchStatus = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/status`);
      setStatus(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching status:', err);
      setError('Failed to fetch status');
    }
  }, []);

  // Start monitoring
  const startMonitoring = async () => {
    try {
      await axios.post(`${API}/monitoring/start`);
      await fetchStatus();
    } catch (err) {
      console.error('Error starting monitoring:', err);
      setError('Failed to start monitoring');
    }
  };

  // Stop monitoring
  const stopMonitoring = async () => {
    try {
      await axios.post(`${API}/monitoring/stop`);
      await fetchStatus();
    } catch (err) {
      console.error('Error stopping monitoring:', err);
      setError('Failed to stop monitoring');
    }
  };

  // Clear all alerts
  const clearAlerts = async () => {
    if (window.confirm('Are you sure you want to clear all alerts?')) {
      try {
        await axios.delete(`${API}/alerts`);
        await fetchAlerts();
        await fetchStatus();
      } catch (err) {
        console.error('Error clearing alerts:', err);
        setError('Failed to clear alerts');
      }
    }
  };

  // Generate mock alert for testing
  const generateMockAlert = async () => {
    try {
      const response = await axios.get(`${API}/test/generate-mock-alert`);
      await fetchAlerts();
      await fetchStatus();
      
      // Show success notification
      const alertData = response.data.alert;
      setNotification({
        type: 'success',
        title: '✅ Test Alert Generated!',
        message: `Created ${alertData.threat_level} threat alert from ${alertData.platform}`,
        details: `Score: ${(alertData.score * 100).toFixed(1)}% | Author: @${alertData.author}`
      });
      
      // Auto-hide notification after 4 seconds
      setTimeout(() => setNotification(null), 4000);
      
    } catch (err) {
      console.error('Error generating mock alert:', err);
      setError('Failed to generate mock alert');
      setNotification({
        type: 'error',
        title: '❌ Error',
        message: 'Failed to generate test alert',
        details: err.message
      });
      setTimeout(() => setNotification(null), 4000);
    }
  };

  // Initial data load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchAlerts(), fetchStatus()]);
      setLoading(false);
    };
    loadData();
  }, [fetchAlerts, fetchStatus]);

  // Set up polling for real-time updates (every 15 seconds)
  useEffect(() => {
    const interval = setInterval(() => {
      fetchAlerts();
      fetchStatus();
    }, 15000);

    return () => clearInterval(interval);
  }, [fetchAlerts, fetchStatus]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-gray-600">Loading VIP Threat Monitoring System...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Notification Popup */}
      <NotificationPopup 
        notification={notification} 
        onClose={() => setNotification(null)} 
      />
      
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">🛡️ VIP Threat Monitoring System</h1>
              <p className="text-gray-600">Real-time social media threat detection and analysis</p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={generateMockAlert}
                className="px-3 py-2 bg-blue-600 text-white rounded-md text-sm font-semibold hover:bg-blue-700"
              >
                🧪 Generate Test Alert
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Monitoring Status */}
        <MonitoringStatus
          status={status}
          onStart={startMonitoring}
          onStop={stopMonitoring}
          onClear={clearAlerts}
        />

        {/* Alerts Section */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Threat Alerts</h2>
            <div className="text-sm text-gray-600">
              {alerts.length} alerts • Updated every 15 seconds
            </div>
          </div>

          {alerts.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎉</div>
              <div className="text-xl font-semibold text-gray-900 mb-2">No Threats Detected</div>
              <div className="text-gray-600">All monitored content appears safe</div>
              <button
                onClick={generateMockAlert}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Generate Test Alert
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {alerts.map((alert) => (
                <ThreatAlert key={alert.id} alert={alert} />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="text-center text-sm text-gray-600">
            VIP Threat Monitoring System • Monitoring: Twitter, Facebook, Instagram
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;