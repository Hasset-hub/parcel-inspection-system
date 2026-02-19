import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import parcelService, { ParcelDetail } from '../services/parcelService';
import { 
  Package, 
  AlertTriangle, 
  CheckCircle, 
  Calendar,
  MapPin,
  Weight,
  Ruler,
  FileText,
  ArrowLeft
} from 'lucide-react';

const ParcelDetailPage: React.FC = () => {
  const { parcelId } = useParams<{ parcelId: string }>();
  const navigate = useNavigate();
  const [parcel, setParcel] = useState<ParcelDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState(false);

  useEffect(() => {
    if (parcelId) {
      loadParcel();
    }
  }, [parcelId]);

  const loadParcel = async () => {
    if (!parcelId) return;
    setLoading(true);
    try {
      const data = await parcelService.getParcelById(parcelId);
      setParcel(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load parcel');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (newStatus: string) => {
    if (!parcelId || !window.confirm(`Change status to ${newStatus}?`)) return;
    
    setUpdatingStatus(true);
    try {
      await parcelService.updateParcelStatus(parcelId, newStatus);
      await loadParcel();
    } catch (err: any) {
      alert('Failed to update status: ' + err.message);
    } finally {
      setUpdatingStatus(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      received: 'bg-blue-100 text-blue-800',
      inspecting: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      damaged: 'bg-red-100 text-red-800',
      quarantine: 'bg-purple-100 text-purple-800',
      stored: 'bg-gray-100 text-gray-800',
      shipped: 'bg-indigo-100 text-indigo-800',
    };
    return styles[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading parcel details...</div>
      </div>
    );
  }

  if (error || !parcel) {
    return (
      <div className="p-6">
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">
          {error || 'Parcel not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/parcels')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {parcel.tracking_number}
            </h1>
            <p className="text-gray-600 mt-1">Parcel Details</p>
          </div>
        </div>
        <span className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusBadge(parcel.status)}`}>
          {parcel.status}
        </span>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Damage Status Card */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Damage Status</h2>
            <div className="flex items-center gap-6">
              {parcel.has_damage ? (
                <>
                  <AlertTriangle className="w-12 h-12 text-red-600" />
                  <div>
                    <p className="text-lg font-medium text-gray-900">Damage Detected</p>
                    <p className="text-sm text-gray-600">
                      Severity: <span className="font-semibold capitalize">{parcel.damage_severity || 'Unknown'}</span>
                    </p>
                    {parcel.damage_value_estimate && (
                      <p className="text-sm text-gray-600">
                        Estimated Value: ${parcel.damage_value_estimate.toFixed(2)}
                      </p>
                    )}
                  </div>
                </>
              ) : (
                <>
                  <CheckCircle className="w-12 h-12 text-green-600" />
                  <div>
                    <p className="text-lg font-medium text-gray-900">No Damage</p>
                    <p className="text-sm text-gray-600">Parcel is in good condition</p>
                  </div>
                </>
              )}
            </div>
            {parcel.auto_resolved && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-900 font-medium">Auto-Resolved</p>
                <p className="text-sm text-blue-700">{parcel.auto_resolution_reason}</p>
              </div>
            )}
          </div>

          {/* Details Card */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Parcel Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <Package className="w-5 h-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-600">Tracking Number</p>
                  <p className="font-mono font-medium">{parcel.tracking_number}</p>
                </div>
              </div>
              
              {parcel.current_location && (
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-600">Current Location</p>
                    <p className="font-medium">{parcel.current_location}</p>
                  </div>
                </div>
              )}

              {parcel.weight_kg && (
                <div className="flex items-start gap-3">
                  <Weight className="w-5 h-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-600">Weight</p>
                    <p className="font-medium">{parcel.weight_kg} kg</p>
                  </div>
                </div>
              )}

              <div className="flex items-start gap-3">
                <Calendar className="w-5 h-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-600">Received</p>
                  <p className="font-medium">
                    {parcel.received_at ? new Date(parcel.received_at).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Inspection History */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Inspection History</h2>
            {!parcel.inspections || parcel.inspections.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No inspections recorded</p>
            ) : (
              <div className="space-y-3">
                {parcel.inspections.map((inspection) => (
                  <div key={inspection.inspection_id} className="border-l-4 border-blue-600 pl-4 py-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">
                          {inspection.inspection_type || 'Standard Inspection'}
                        </p>
                        <p className="text-sm text-gray-600">
                          Status: <span className="font-medium">{inspection.overall_status}</span>
                          {inspection.damage_count > 0 && (
                            <span className="ml-2 text-red-600">
                              • {inspection.damage_count} damage(s) detected
                            </span>
                          )}
                        </p>
                      </div>
                      <div className="text-right text-sm text-gray-500">
                        {inspection.completed_at 
                          ? new Date(inspection.completed_at).toLocaleString()
                          : new Date(inspection.created_at).toLocaleString()
                        }
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Actions */}
        <div className="space-y-6">
          {/* Status Actions */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions</h2>
            <div className="space-y-2">
              <button
                onClick={() => handleStatusUpdate('approved')}
                disabled={updatingStatus || parcel.status === 'approved'}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Approve Parcel
              </button>
              <button
                onClick={() => handleStatusUpdate('quarantine')}
                disabled={updatingStatus || parcel.status === 'quarantine'}
                className="w-full px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Move to Quarantine
              </button>
              <button
                onClick={() => handleStatusUpdate('damaged')}
                disabled={updatingStatus || parcel.status === 'damaged'}
                className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Mark as Damaged
              </button>
              <button
                onClick={() => handleStatusUpdate('stored')}
                disabled={updatingStatus || parcel.status === 'stored'}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Move to Storage
              </button>
              <button
                onClick={() => navigate(`/inspections/new?parcel=${parcelId}`)}
                className="w-full px-4 py-2 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
              >
                New Inspection
              </button>
            </div>
          </div>

          {/* Timestamps */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Timeline</h2>
            <div className="space-y-3 text-sm">
              {parcel.received_at && (
                <div>
                  <p className="text-gray-600">Received</p>
                  <p className="font-medium">{new Date(parcel.received_at).toLocaleString()}</p>
                </div>
              )}
              {parcel.inspected_at && (
                <div>
                  <p className="text-gray-600">Inspected</p>
                  <p className="font-medium">{new Date(parcel.inspected_at).toLocaleString()}</p>
                </div>
              )}
              {parcel.updated_at && (
                <div>
                  <p className="text-gray-600">Last Updated</p>
                  <p className="font-medium">{new Date(parcel.updated_at).toLocaleString()}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParcelDetailPage;
