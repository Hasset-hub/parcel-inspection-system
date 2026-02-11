export interface User {
  user_id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'SCANNER' | 'INSPECTOR' | 'SUPERVISOR' | 'ADMIN';
  is_active: boolean;
}

export interface DashboardStats {
  total_parcels: number;
  damaged_parcels: number;
  auto_resolved: number;
  completed_inspections: number;
  damage_rate: number;
  auto_resolution_rate: number;
  generated_at: string;
}

export interface Parcel {
  parcel_id: string;
  tracking_number: string;
  status: string;
  has_damage: boolean;
  damage_severity?: string;
  received_at: string;
}

export interface Inspection {
  inspection_id: string;
  parcel_id: string;
  overall_status: string;
  has_damage: boolean;
  damage_count: number;
  images_received: number;
  started_at: string;
}
