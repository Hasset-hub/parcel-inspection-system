import api from './api';

export interface DamageTrendData {
  date: string;
  count: number;
  severity_avg: number;
}

export interface DamageByTypeData {
  damage_type: string;
  count: number;
  percentage: number;
}

export interface SupplierPerformanceData {
  supplier_name: string;
  total_parcels: number;
  damaged_parcels: number;
  damage_rate: number;
}

export interface DashboardStats {
  total_inspections: number;
  damaged_parcels: number;
  damage_rate: number;
  pending_inspections: number;
  avg_processing_time: number;
}

class AnalyticsService {
  // Get dashboard summary stats
  async getDashboardStats(startDate?: string, endDate?: string): Promise<DashboardStats> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/api/v1/analytics/dashboard-stats?${params}`);
    return response.data;
  }

  // Get damage trends over time
  async getDamageTrends(days: number = 30): Promise<DamageTrendData[]> {
    const response = await api.get(`/api/v1/analytics/damage-trends?days=${days}`);
    return response.data;
  }

  // Get damage distribution by type
  async getDamageByType(startDate?: string, endDate?: string): Promise<DamageByTypeData[]> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/api/v1/analytics/damage-by-type?${params}`);
    return response.data;
  }

  // Get supplier performance
  async getSupplierPerformance(limit: number = 10): Promise<SupplierPerformanceData[]> {
    const response = await api.get(`/api/v1/analytics/supplier-performance?limit=${limit}`);
    return response.data;
  }
}

export default new AnalyticsService();
