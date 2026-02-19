import api from './api';

export interface Parcel {
  parcel_id: string;
  tracking_number: string;
  status: string;
  has_damage: boolean;
  damage_severity?: string;
  created_at: string;
  updated_at: string;
  auto_resolved: boolean;
  resolution_reason?: string;
}

export interface ParcelDetail extends Parcel {
  inspections?: any[];
  damage_detections?: any[];
}

class ParcelService {
  async getParcels(params?: {
    status?: string;
    has_damage?: boolean;
    page?: number;
    limit?: number;
    search?: string;
  }): Promise<{ parcels: Parcel[]; total: number }> {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.has_damage !== undefined) queryParams.append('has_damage', String(params.has_damage));
    if (params?.page) queryParams.append('page', String(params.page));
    if (params?.limit) queryParams.append('limit', String(params.limit));
    if (params?.search) queryParams.append('search', params.search);

    const response = await api.get(`/api/v1/parcels?${queryParams}`);
    return response.data;
  }

  async getParcelById(parcelId: string): Promise<ParcelDetail> {
    const response = await api.get(`/api/v1/parcels/${parcelId}`);
    return response.data;
  }

  async updateParcelStatus(parcelId: string, status: string): Promise<Parcel> {
    const response = await api.patch(`/api/v1/parcels/${parcelId}/status`, { status });
    return response.data;
  }

  async bulkUpdateStatus(parcelIds: string[], status: string): Promise<void> {
    await api.post('/api/v1/parcels/bulk-update', { parcel_ids: parcelIds, status });
  }
}

export default new ParcelService();
