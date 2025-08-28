import React, { useState } from 'react';
import { useAuth } from '../App';
import { Button } from './ui/button';
import { 
  Menu, 
  X, 
  Home, 
  Users, 
  BookOpen, 
  GraduationCap, 
  Settings, 
  LogOut,
  School,
  ClipboardList,
  BarChart3,
  Calendar,
  UserCheck,
  FileText
} from 'lucide-react';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const getMenuItems = (role) => {
    const menus = {
      admin: [
        { icon: Home, label: 'Dashboard', href: '/dashboard' },
        { icon: Users, label: 'Kelola Siswa', href: '/admin/siswa' },
        { icon: UserCheck, label: 'Kelola Guru', href: '/admin/guru' },
        { icon: School, label: 'Kelola Kelas', href: '/admin/kelas' },
        { icon: BookOpen, label: 'Mata Pelajaran', href: '/admin/mapel' },
        { icon: Calendar, label: 'Tahun Ajaran', href: '/admin/tahun-ajaran' },
        { icon: BarChart3, label: 'Laporan', href: '/admin/laporan' },
        { icon: FileText, label: 'Cetak Rapor', href: '/admin/rapor' },
        { icon: Settings, label: 'Pengaturan', href: '/admin/settings' }
      ],
      guru_mapel: [
        { icon: Home, label: 'Dashboard', href: '/dashboard' },
        { icon: ClipboardList, label: 'Input Nilai', href: '/guru/nilai' },
        { icon: BookOpen, label: 'Mata Pelajaran', href: '/guru/mapel' },
        { icon: BarChart3, label: 'Rekap Nilai', href: '/guru/rekap' }
      ],
      guru_pkl: [
        { icon: Home, label: 'Dashboard', href: '/dashboard' },
        { icon: ClipboardList, label: 'Nilai PKL', href: '/pkl/nilai' },
        { icon: Users, label: 'Siswa PKL', href: '/pkl/siswa' }
      ],
      fasilitator_p5: [
        { icon: Home, label: 'Dashboard', href: '/dashboard' },
        { icon: ClipboardList, label: 'Nilai P5', href: '/p5/nilai' },
        { icon: Users, label: 'Projek P5', href: '/p5/projek' }
      ],
      guru_ekstra: [
        { icon: Home, label: 'Dashboard', href: '/dashboard' },
        { icon: ClipboardList, label: 'Nilai Ekstra', href: '/ekstra/nilai' },
        { icon: Users, label: 'Kegiatan Ekstra', href: '/ekstra/kegiatan' }
      ],
      wali_kelas: [
        { icon: Home, label: 'Dashboard', href: '/dashboard' },
        { icon: Users, label: 'Daftar Siswa', href: '/wali/siswa' },
        { icon: Calendar, label: 'Kehadiran', href: '/wali/kehadiran' },
        { icon: ClipboardList, label: 'Catatan Siswa', href: '/wali/catatan' },
        { icon: FileText, label: 'Cetak Rapor', href: '/wali/rapor' }
      ]
    };
    return menus[role] || [];
  };

  const handleLogout = () => {
    logout();
  };

  const Sidebar = ({ className = '' }) => (
    <div className={`bg-white border-r border-gray-200 ${className}`}>
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center gap-3 p-6 border-b border-gray-200">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <GraduationCap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-gray-900">E-Rapor SMK</h1>
            <p className="text-xs text-gray-600">Kurikulum Merdeka</p>
          </div>
        </div>

        {/* User Info */}
        <div className="p-4 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-blue-700">
                {user?.name?.charAt(0)?.toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user?.name}
              </p>
              <p className="text-xs text-gray-600 truncate">
                {user?.role === 'admin' && 'Administrator'}
                {user?.role === 'guru_mapel' && 'Guru Mapel'}
                {user?.role === 'guru_pkl' && 'Guru PKL'}
                {user?.role === 'fasilitator_p5' && 'Fasilitator P5'}
                {user?.role === 'guru_ekstra' && 'Guru Ekstra'}
                {user?.role === 'wali_kelas' && 'Wali Kelas'}
              </p>
            </div>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 overflow-y-auto p-4">
          <ul className="space-y-2">
            {getMenuItems(user?.role).map((item, index) => (
              <li key={index}>
                <a
                  href={item.href}
                  className="flex items-center gap-3 px-3 py-2 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors group"
                  onClick={(e) => {
                    e.preventDefault();
                    setSidebarOpen(false);
                  }}
                >
                  <item.icon className="w-5 h-5 text-gray-500 group-hover:text-gray-700" />
                  <span className="font-medium">{item.label}</span>
                </a>
              </li>
            ))}
          </ul>
        </nav>

        {/* Logout Button */}
        <div className="p-4 border-t border-gray-200">
          <Button
            variant="ghost"
            onClick={handleLogout}
            className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Keluar
          </Button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Desktop Sidebar */}
      <div className="hidden lg:block w-64">
        <Sidebar />
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="lg:hidden fixed inset-0 z-50 bg-black bg-opacity-50"
          onClick={() => setSidebarOpen(false)}
        >
          <div className="w-64 h-full" onClick={e => e.stopPropagation()}>
            <Sidebar />
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Navigation */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden"
              >
                <Menu className="w-5 h-5" />
              </Button>
              <div className="hidden lg:block">
                <h2 className="text-xl font-semibold text-gray-900">Dashboard</h2>
                <p className="text-sm text-gray-600">
                  {new Date().toLocaleDateString('id-ID', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right hidden md:block">
                <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                <p className="text-xs text-gray-600">{user?.email}</p>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;