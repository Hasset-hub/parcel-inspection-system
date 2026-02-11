import { useState, useEffect } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import authService from '../../services/authService';
import { User } from '../../types';

const DashboardLayout = () => {
  const [user, setUser] = useState<User | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    authService.getCurrentUser()
      .then(setUser)
      .catch(() => navigate('/login'));
  }, [navigate]);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊' },
    { name: 'Inspections', href: '/inspections', icon: '🔍' },
    { name: 'Parcels', href: '/parcels', icon: '📦' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg">
        <div className="flex flex-col h-full">
          <div className="h-16 px-6 bg-blue-600 flex items-center">
            <span className="text-xl font-bold text-white">Parcel Inspect</span>
          </div>

          <nav className="flex-1 px-4 py-6 space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600"
              >
                <span className="text-xl mr-3">{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </Link>
            ))}
          </nav>

          <div className="p-4 border-t">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-semibold">{user?.full_name?.[0] || 'U'}</span>
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium">{user?.full_name}</p>
                <p className="text-xs text-gray-500">{user?.role}</p>
              </div>
              <button onClick={() => authService.logout()} className="text-gray-400 hover:text-gray-600">
                🚪
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="ml-64">
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
