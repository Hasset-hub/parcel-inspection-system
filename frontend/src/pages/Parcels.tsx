import React, { useEffect, useState } from 'react';
import parcelService, { Parcel } from '../services/parcelService';
import { useToast } from '../contexts/ToastContext';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import { Search, Package, AlertTriangle, CheckCircle, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Parcels: React.FC = () => {
  const navigate = useNavigate();
  const { showError } = useToast();
  
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [damageFilter, setDamageFilter] = useState<string>('');
  const [selectedParcels, setSelectedParcels] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadParcels();
  }, [statusFilter, damageFilter]);

  const loadParcels = async () => {
    setLoading(true);
    try {
      const filters: any = {};
      if (statusFilter) filters.status = statusFilter;
      if (damageFilter) filters.has_damage = damageFilter === 'true';
      if (search) filters.search = search;

      const data = await parcelService.getParcels(filters);
      setParcels(data.parcels || []);
    } catch (error: any) {
      showError('Failed to load parcels: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadParcels();
  };

  const toggleSelectParcel = (parcelId: string) => {
    const newSelected = new Set(selectedParcels);
    if (newSelected.has(parcelId)) {
      newSelected.delete(parcelId);
    } else {
      newSelected.add(parcelId);
    }
    setSelectedParcels(newSelected);
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      in_transit: 'bg-blue-100 text-blue-800',
    };
    return styles[status] || 'bg-gray-100 text-gray-800';
  };

  const getSeverityIcon = (parcel: Parcel) => {
    if (!parcel.has_damage) {
      return <CheckCircle className="w-5 h-5 text-green-600" />;
    }
    if (parcel.damage_severity === 'severe') {
      return <AlertTriangle className="w-5 h-5 text-red-600" />;
    }
    return <AlertTriangle className="w-5 h-5 text-amber-600" />;
  };

  if (loading) {
    return <LoadingSpinner fullScreen text="Loading parcels..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Parcel Management</h1>
          <p className="text-gray-600 mt-1">Track and manage all parcels</p>
        </div>
        <button
          onClick={() => navigate('/inspections/new')}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" />
          New Inspection
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex gap-4">
          <form onSubmit={handleSearch} className="flex-1 flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by tracking number..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Search
            </button>
          </form>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="received">Received</option>
            <option value="inspecting">Inspecting</option>
            <option value="approved">Approved</option>
            <option value="damaged">Damaged</option>
            <option value="quarantine">Quarantine</option>
            <option value="stored">Stored</option>
          </select>

          <select
            value={damageFilter}
            onChange={(e) => setDamageFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Damage</option>
            <option value="true">Damaged</option>
            <option value="false">No Damage</option>
          </select>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedParcels.size > 0 && (
        <div className="bg-blue-50 p-4 rounded-lg flex items-center justify-between">
          <span className="text-sm text-gray-700">
            {selectedParcels.size} parcel(s) selected
          </span>
          <div className="flex gap-2">
            <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
              Approve Selected
            </button>
            <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm">
              Reject Selected
            </button>
          </div>
        </div>
      )}

      {/* Parcels Table or Empty State */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {parcels.length === 0 ? (
          <EmptyState
            icon={Package}
            title="No parcels found"
            description="There are no parcels matching your current filters. Try adjusting your search criteria or create a new inspection."
            action={{
              label: "New Inspection",
              onClick: () => navigate('/inspections/new')
            }}
          />
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left">
                  <input type="checkbox" className="rounded" />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tracking Number</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Damage</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {parcels.map((parcel) => (
                <tr key={parcel.parcel_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <input
                      type="checkbox"
                      checked={selectedParcels.has(parcel.parcel_id)}
                      onChange={() => toggleSelectParcel(parcel.parcel_id)}
                      className="rounded"
                    />
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(parcel.status)}`}>
                      {parcel.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-sm">{parcel.tracking_number}</td>
                  <td className="px-6 py-4">{getSeverityIcon(parcel)}</td>
                  <td className="px-6 py-4 text-sm capitalize">{parcel.damage_severity || 'N/A'}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(parcel.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => navigate(`/parcels/${parcel.parcel_id}`)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium hover:underline"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Parcels;
