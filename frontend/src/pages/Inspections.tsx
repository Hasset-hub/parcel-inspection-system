import { Link } from 'react-router-dom';
import { Plus, Search } from 'lucide-react';

const Inspections = () => {
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Inspections</h1>
        <Link
          to="/inspections/new"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-5 h-5 mr-2" />
          New Inspection
        </Link>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by tracking number..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Empty State */}
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="text-6xl mb-4">🔍</div>
        <h3 className="text-xl font-semibold mb-2">No Inspections Yet</h3>
        <p className="text-gray-600 mb-6">
          Start your first inspection by uploading parcel images
        </p>
        <Link
          to="/inspections/new"
          className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-5 h-5 mr-2" />
          Create First Inspection
        </Link>
      </div>
    </div>
  );
};

export default Inspections;
