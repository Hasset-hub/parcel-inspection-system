import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { SupplierPerformanceData } from '../../services/analyticsService';

interface Props {
  data: SupplierPerformanceData[];
  loading?: boolean;
}

const SupplierPerformanceChart: React.FC<Props> = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading chart...</div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">No data available</div>
      </div>
    );
  }

  // Format data for chart
  const chartData = data.map(supplier => ({
    ...supplier,
    damage_rate_percent: (supplier.damage_rate * 100).toFixed(1)
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" tick={{ fontSize: 12 }} />
        <YAxis 
          dataKey="supplier_name" 
          type="category" 
          tick={{ fontSize: 12 }}
          width={120}
        />
        <Tooltip />
        <Legend />
        <Bar 
          dataKey="damage_rate_percent" 
          fill="#ef4444" 
          name="Damage Rate (%)"
          radius={[0, 8, 8, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default SupplierPerformanceChart;
