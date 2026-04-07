import React from 'react';
import { Link } from 'react-router-dom';
import { Map, AlertTriangle, Navigation, MessageCircle, Activity, Shield, Users, Clock, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { getCurrentLocation } from '../utils/geolocation';
import { getSafetyPrediction, checkApiHealth } from '../services/safetyService';
import { getSafetyColor, getSafetyBgColor, getSafetyTextColor } from '../utils/colorUtils';

const Dashboard = () => {
  const [status, setStatus] = useState("Loading...");
  const [loading, setLoading] = useState(true);
  const [safetyData, setSafetyData] = useState(null);
  const [error, setError] = useState(null);
  const [currentLocation, setCurrentLocation] = useState(null);

  useEffect(() => {
    // Check API health
    checkApiHealth()
      .then((data) => {
        setStatus(data.message || "SafeSphere API is running");
      })
      .catch((err) => {
        console.error(err);
        setStatus("Backend not reachable");
      });

    // Get current location and fetch safety data
    fetchSafetyData();
  }, []);

  const fetchSafetyData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get user's current location
      const location = await getCurrentLocation();
      setCurrentLocation(location);

      // Fetch safety prediction
      const data = await getSafetyPrediction(location.latitude, location.longitude);
      setSafetyData(data);
    } catch (err) {
      console.error('Error fetching safety data:', err);
      setError(err.message || 'Failed to fetch safety data');
      
      // If geolocation fails, use default Mumbai coordinates
      if (err.message.includes('Geolocation') || err.message.includes('denied')) {
        const defaultLocation = { latitude: 19.1197, longitude: 72.8464 }; // Mumbai default
        setCurrentLocation(defaultLocation);
        try {
          const data = await getSafetyPrediction(defaultLocation.latitude, defaultLocation.longitude);
          setSafetyData(data);
        } catch (apiErr) {
          setError('Failed to fetch safety data. Please ensure the API server is running.');
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      icon: <Navigation className="w-6 h-6" />,
      title: 'Safe Route',
      description: 'Find the safest path',
      href: '/safe-route',
      color: 'bg-blue-500'
    },
    {
      icon: <AlertTriangle className="w-6 h-6" />,
      title: 'Emergency SOS',
      description: 'Send emergency alert',
      href: '/emergency',
      color: 'bg-red-500'
    },
    {
      icon: <MessageCircle className="w-6 h-6" />,
      title: 'Report Incident',
      description: 'Report safety concern',
      href: '/report',
      color: 'bg-yellow-500'
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: 'SafeBot',
      description: 'AI safety assistant',
      href: '/safebot',
      color: 'bg-green-500'
    }
  ];

  const safetyStats = [
    { 
      label: 'Current Risk Level', 
      value: safetyData ? (safetyData.average_safety_score >= 7 ? 'Low' : safetyData.average_safety_score >= 4 ? 'Medium' : 'High') : 'N/A', 
      color: safetyData ? (safetyData.average_safety_score >= 7 ? 'text-green-600' : safetyData.average_safety_score >= 4 ? 'text-yellow-600' : 'text-red-600') : 'text-gray-600', 
      bg: safetyData ? (safetyData.average_safety_score >= 7 ? 'bg-green-50' : safetyData.average_safety_score >= 4 ? 'bg-yellow-50' : 'bg-red-50') : 'bg-gray-50' 
    },
    { 
      label: 'Nearby Locations', 
      value: safetyData ? safetyData.locations.length : '0', 
      color: 'text-blue-600', 
      bg: 'bg-blue-50' 
    },
    { 
      label: 'Average Safety Score', 
      value: safetyData ? `${safetyData.average_safety_score.toFixed(1)}/10` : 'N/A', 
      color: 'text-purple-600', 
      bg: 'bg-purple-50' 
    },
    { 
      label: 'Community Members', 
      value: '1,247', 
      color: 'text-gray-600', 
      bg: 'bg-gray-50' 
    }
  ];

  const recentAlerts = [
    {
      type: 'warning',
      message: 'Suspicious activity reported near Central Park',
      time: '2 minutes ago',
      location: 'Central Park, NYC'
    },
    {
      type: 'info',
      message: 'Safe route available to your destination',
      time: '5 minutes ago',
      location: 'Current Location'
    },
    {
      type: 'success',
      message: 'Emergency contact updated successfully',
      time: '1 hour ago',
      location: 'Profile Settings'
    }
  ];

  const safetyTips = [
    'Stay in well-lit areas when walking at night',
    'Share your location with trusted contacts',
    'Be aware of your surroundings',
    'Trust your instincts - if something feels wrong, it probably is'
  ];

  // Prepare chart data
  const chartData = safetyData?.locations.map((loc, index) => ({
    name: loc.name.length > 15 ? loc.name.substring(0, 15) + '...' : loc.name,
    fullName: loc.name,
    safety_score: loc.safety_score,
    color: getSafetyColor(loc.safety_score)
  })) || [];

  // Get safety score for banner
  const averageSafetyScore = safetyData?.average_safety_score || 0;
  const safetyPercentage = safetyData?.average_safety_percentage || 0;
  const bannerBgColor = getSafetyColor(averageSafetyScore);
  const bannerTextColor = averageSafetyScore >= 6 ? 'text-gray-900' : 'text-white';

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <p className="mb-4 text-sm text-gray-600">Backend Status: {status}</p>
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Safety Dashboard</h1>
          <p className="text-gray-600">Monitor your safety status and access quick actions</p>
        </div>

        {/* Safety Status Banner */}
        <div 
          className="rounded-xl p-6 mb-8 text-white transition-all duration-300"
          style={{ backgroundColor: bannerBgColor }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8" />
              <div>
                <h3 className={`text-xl font-semibold ${bannerTextColor}`}>
                  Safety Status: {averageSafetyScore >= 7 ? 'Secure' : averageSafetyScore >= 4 ? 'Moderate' : 'At Risk'}
                </h3>
                <p className={`${bannerTextColor} opacity-90`}>
                  {loading ? 'Loading safety data...' : currentLocation 
                    ? `Based on your current location (${currentLocation.latitude.toFixed(4)}, ${currentLocation.longitude.toFixed(4)})`
                    : 'Your current location is being analyzed'}
                </p>
              </div>
            </div>
            <div className="text-right">
              {loading ? (
                <Loader2 className="w-8 h-8 animate-spin mx-auto" />
              ) : (
                <>
                  <div className={`text-2xl font-bold ${bannerTextColor}`}>
                    {safetyPercentage}%
                  </div>
                  <div className={`${bannerTextColor} opacity-90`}>
                    Safety Score
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <p>{error}</p>
              <button
                onClick={fetchSafetyData}
                className="text-red-600 hover:text-red-800 font-medium text-sm"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {quickActions.map((action, index) => (
            <Link
              aria-label={action.title}
              key={index}
              to={action.href}
              className="bg-white rounded-xl shadow p-4 hover:shadow-lg transition-all duration-200 transform hover:-translate-y-1"
            >
              <div className={`w-12 h-12 ${action.color} rounded-lg flex items-center justify-center text-white mb-4`}>
                {action.icon}
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">{action.title}</h3>
              <p className="text-sm text-gray-600">{action.description}</p>
            </Link>
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Safety Chart */}
            <div className="bg-white rounded-xl shadow p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Nearby Locations Safety Scores</h2>
                <button 
                  onClick={fetchSafetyData}
                  className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center gap-2"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    'Refresh Data'
                  )}
                </button>
              </div>
              
              {loading ? (
                <div className="h-80 flex items-center justify-center">
                  <Loader2 className="w-12 h-12 animate-spin text-gray-400" />
                </div>
              ) : error ? (
                <div className="h-80 flex items-center justify-center text-gray-500">
                  <p>Unable to load chart data</p>
                </div>
              ) : chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 80 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="name" 
                      angle={-45} 
                      textAnchor="end" 
                      height={100}
                      interval={0}
                    />
                    <YAxis 
                      domain={[0, 10]}
                      label={{ value: 'Safety Score', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip 
                      formatter={(value, name, props) => [
                        `${value}/10`,
                        props.payload.fullName
                      ]}
                      labelFormatter={(label) => `Location: ${label}`}
                    />
                    <Legend />
                    <Bar dataKey="safety_score" name="Safety Score" radius={[8, 8, 0, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-80 flex items-center justify-center text-gray-500">
                  <p>No data available</p>
                </div>
              )}
            </div>

            {/* Safety Map */}
            <div className="bg-white rounded-xl shadow p-4">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Safety Map</h2>
                <button className="text-blue-600 hover:text-blue-700 font-medium">
                  View Full Map
                </button>
              </div>
              <div className="bg-gray-100 rounded-lg h-80 flex items-center justify-center">
                <div className="text-center">
                  <Map className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Interactive safety map with real-time data</p>
                  <p className="text-sm text-gray-500 mt-2">Green zones: Safe • Red zones: High risk</p>
                </div>
              </div>
            </div>

            {/* Safety Statistics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {safetyStats.map((stat, index) => (
                <div key={index} className={`${stat.bg} rounded-lg p-4 text-center`}>
                  <div className={`text-2xl font-bold ${stat.color} mb-1`}>
                    {stat.value}
                  </div>
                  <div className="text-sm text-gray-600">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Recent Alerts */}
            <div className="bg-white rounded-xl shadow p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Alerts</h3>
              <div className="space-y-3">
                {recentAlerts.map((alert, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50">
                    <div className={`w-2 h-2 rounded-full mt-2 ${
                      alert.type === 'warning' ? 'bg-yellow-500' :
                      alert.type === 'info' ? 'bg-blue-500' : 'bg-green-500'
                    }`}></div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-900 mb-1">{alert.message}</p>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>{alert.location}</span>
                        <span className="flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {alert.time}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Safety Tips */}
            <div className="bg-white rounded-xl shadow p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Safety Tips</h3>
              <div className="space-y-3">
                {safetyTips.map((tip, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                    <p className="text-sm text-gray-600">{tip}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Community Activity */}
            <div className="bg-white rounded-xl shadow p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Community Activity</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <Users className="w-4 h-4 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Active Users</p>
                      <p className="text-xs text-gray-500">In your area</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-blue-600">47</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <Activity className="w-4 h-4 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Reports Today</p>
                      <p className="text-xs text-gray-500">Community reports</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-green-600">12</div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

