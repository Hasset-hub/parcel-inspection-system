import { useEffect, useState } from 'react';
import api from '../services/api';
import type { DashboardStats } from '../types/index';

const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<DashboardStats>('/api/v1/analytics/dashboard')
      .then(res => setStats(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center">Loading...</div>;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">Total Parcels</p>
          <p className="text-3xl font-bold">{stats?.total_parcels || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">Damaged</p>
          <p className="text-3xl font-bold text-red-600">{stats?.damaged_parcels || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">Auto Resolved</p>
          <p className="text-3xl font-bold text-green-600">{stats?.auto_resolved || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">Inspections</p>
          <p className="text-3xl font-bold">{stats?.completed_inspections || 0}</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
