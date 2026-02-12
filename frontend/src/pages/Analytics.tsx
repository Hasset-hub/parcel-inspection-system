import React, { useEffect, useState } from 'react';
import analyticsService, {
  DamageTrendData,
  DamageByTypeData,
  SupplierPerformanceData
} from '../services/analyticsService';
import DamageTrendChart from '../components/charts/DamageTrendChart';
import DamageTypeChart from '../components/charts/DamageTypeChart';
import SupplierPerformanceChart from '../components/charts/SupplierPerformanceChart';
import { Calendar, Download, TrendingUp, Package, AlertTriangle } from 'lucide-react';

const Analytics: React.FC = () => {
  const [damageTrends, setDamageTrends] = useState<DamageTrendData[]>([]);
  const [damageByType, setDamageByType] = useState<DamageByTypeData[]>([]);
  const [supplierPerformance, setSupplierPerformance] = useState<SupplierPerformanceData[]>([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState(30);

  useEffect(() => {
    loadAnalytics();
  }, [dateRange]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const [trends, types, suppliers] = await Promise.all([
        analyticsService.getDamageTrends(dateRange),
        analyticsService.getDamageByType(),
        analyticsService.getSupplierPerformance()
      ]);
      setDamageTrends(trends);
      setDamageByType(types);
      setSupplierPerformance(suppliers);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-1">Damage detection insights and trends</p>
        </div>
        <div className="flex gap-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last year</option>
          </select>
          <button
            onClick={loadAnalytics}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            Export Report
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Inspections</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">1,234</p>
            </div>
            <Package className="w-8 h-8 text-blue-600" />
          </div>
          <p className="text-xs text-green-600 mt-2">↑ 12% from last period</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Damaged Parcels</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">187</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
          <p className="text-xs text-red-600 mt-2">↑ 5% from last period</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Damage Rate</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">15.2%</p>
            </div>
            <TrendingUp className="w-8 h-8 text-amber-600" />
          </div>
          <p className="text-xs text-amber-600 mt-2">↑ 2.1% from last period</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Processing Time</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">2.3s</p>
            </div>
            <Calendar className="w-8 h-8 text-green-600" />
          </div>
          <p className="text-xs text-green-600 mt-2">↓ 45% from last period</p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Damage Trends Over Time</h2>
          <DamageTrendChart data={damageTrends} loading={loading} />
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Damage Distribution by Type</h2>
          <DamageTypeChart data={damageByType} loading={loading} />
        </div>
      </div>

      {/* Supplier Performance */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Supplier Performance (Top 10)</h2>
        <SupplierPerformanceChart data={supplierPerformance} loading={loading} />
      </div>
    </div>
  );
};

export default Analytics;
