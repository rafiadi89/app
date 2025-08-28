import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../App';
import Layout from './Layout';
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { 
  Users, 
  BookOpen, 
  GraduationCap, 
  School, 
  ClipboardList,
  BarChart3,
  Calendar,
  Bell,
  TrendingUp,
  UserCheck
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
    initializeDefaultData();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
      toast.error('Gagal memuat statistik dashboard');
    } finally {
      setLoading(false);
    }
  };

  const initializeDefaultData = async () => {
    if (user?.role === 'admin') {
      try {
        await axios.post(`${API}/init/default-data`);
        console.log('Default data initialized');
      } catch (error) {
        // Silently handle if data already exists
        console.log('Default data already exists or error occurred');
      }
    }
  };

  const getRoleTitle = (role) => {
    const roleTitles = {
      'admin': 'Administrator Sistem',
      'guru_mapel': 'Guru Mata Pelajaran',
      'guru_pkl': 'Guru Praktik Kerja Lapangan',
      'fasilitator_p5': 'Fasilitator Projek P5',
      'guru_ekstra': 'Guru Ekstrakurikuler',
      'wali_kelas': 'Wali Kelas'
    };
    return roleTitles[role] || role;
  };

  const getWelcomeMessage = (role) => {
    const messages = {
      'admin': 'Kelola data sekolah dan monitor aktivitas seluruh sistem.',
      'guru_mapel': 'Input nilai mata pelajaran dan kelola penilaian siswa.',
      'guru_pkl': 'Kelola penilaian Praktik Kerja Lapangan siswa kelas XII.',
      'fasilitator_p5': 'Input penilaian Projek Penguatan Profil Pelajar Pancasila.',
      'guru_ekstra': 'Kelola penilaian kegiatan ekstrakurikuler siswa.',
      'wali_kelas': 'Monitor kehadiran, catatan, dan cetak rapor siswa di kelas Anda.'
    };
    return messages[role] || 'Selamat datang di sistem E-Rapor SMK.';
  };

  const renderAdminStats = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <Card className="border-l-4 border-l-blue-500 hover:shadow-lg transition-shadow">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Total Siswa</p>
              <p className="text-3xl font-bold text-blue-600">
                {loading ? '...' : stats.total_siswa || 0}
              </p>
            </div>
            <Users className="w-8 h-8 text-blue-500" />
          </div>
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-green-500 hover:shadow-lg transition-shadow">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Total Guru</p>
              <p className="text-3xl font-bold text-green-600">
                {loading ? '...' : stats.total_guru || 0}
              </p>
            </div>
            <UserCheck className="w-8 h-8 text-green-500" />
          </div>
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-purple-500 hover:shadow-lg transition-shadow">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Total Kelas</p>
              <p className="text-3xl font-bold text-purple-600">
                {loading ? '...' : stats.total_kelas || 0}
              </p>
            </div>
            <School className="w-8 h-8 text-purple-500" />
          </div>
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-orange-500 hover:shadow-lg transition-shadow">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Mata Pelajaran</p>
              <p className="text-3xl font-bold text-orange-600">
                {loading ? '...' : stats.total_mapel || 0}
              </p>
            </div>
            <BookOpen className="w-8 h-8 text-orange-500" />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderWaliKelasStats = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      <Card className="border-l-4 border-l-blue-500 hover:shadow-lg transition-shadow">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Siswa di Kelas</p>
              <p className="text-3xl font-bold text-blue-600">
                {loading ? '...' : stats.siswa_di_kelas || 0}
              </p>
            </div>
            <Users className="w-8 h-8 text-blue-500" />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const getQuickActions = (role) => {
    const actions = {
      'admin': [
        { icon: Users, label: 'Kelola Siswa', href: '/admin/siswa', color: 'bg-blue-500' },
        { icon: UserCheck, label: 'Kelola Guru', href: '/admin/guru', color: 'bg-green-500' },
        { icon: School, label: 'Kelola Kelas', href: '/admin/kelas', color: 'bg-purple-500' },
        { icon: BookOpen, label: 'Kelola Mapel', href: '/admin/mapel', color: 'bg-orange-500' },
        { icon: BarChart3, label: 'Laporan', href: '/admin/laporan', color: 'bg-indigo-500' },
        { icon: ClipboardList, label: 'Cetak Rapor', href: '/admin/rapor', color: 'bg-red-500' }
      ],
      'guru_mapel': [
        { icon: ClipboardList, label: 'Input Nilai', href: '/guru/nilai', color: 'bg-blue-500' },
        { icon: BookOpen, label: 'Mata Pelajaran', href: '/guru/mapel', color: 'bg-green-500' },
        { icon: BarChart3, label: 'Rekap Nilai', href: '/guru/rekap', color: 'bg-purple-500' }
      ],
      'wali_kelas': [
        { icon: Users, label: 'Daftar Siswa', href: '/wali/siswa', color: 'bg-blue-500' },
        { icon: Calendar, label: 'Kehadiran', href: '/wali/kehadiran', color: 'bg-green-500' },
        { icon: ClipboardList, label: 'Catatan', href: '/wali/catatan', color: 'bg-purple-500' },
        { icon: GraduationCap, label: 'Cetak Rapor', href: '/wali/rapor', color: 'bg-red-500' }
      ]
    };
    return actions[role] || [];
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-blue-500 to-green-500 rounded-xl p-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">
                Selamat Datang, {user?.name}!
              </h1>
              <p className="text-lg opacity-90 mb-1">
                {getRoleTitle(user?.role)}
              </p>
              <p className="opacity-80">
                {getWelcomeMessage(user?.role)}
              </p>
            </div>
            <div className="hidden md:block">
              <GraduationCap className="w-24 h-24 opacity-20" />
            </div>
          </div>
        </div>

        {/* Statistics Cards */}
        {user?.role === 'admin' && renderAdminStats()}
        {user?.role === 'wali_kelas' && renderWaliKelasStats()}

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Aksi Cepat
            </CardTitle>
            <CardDescription>
              Fitur yang sering digunakan untuk mempercepat pekerjaan Anda
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {getQuickActions(user?.role).map((action, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  className="h-auto p-4 flex flex-col items-center gap-2 hover:bg-gray-50 border border-gray-200 hover:border-gray-300 transition-all"
                  onClick={() => toast.info(`Fitur ${action.label} segera hadir!`)}
                >
                  <div className={`w-10 h-10 rounded-lg ${action.color} flex items-center justify-center`}>
                    <action.icon className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-sm font-medium text-center">{action.label}</span>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="w-5 h-5" />
                Pengumuman
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="p-3 bg-blue-50 border-l-4 border-l-blue-500 rounded">
                  <p className="text-sm font-medium text-blue-900">Sistem E-Rapor SMK Aktif</p>
                  <p className="text-xs text-blue-700 mt-1">
                    Sistem telah siap digunakan untuk input nilai semester ini.
                  </p>
                </div>
                <div className="p-3 bg-green-50 border-l-4 border-l-green-500 rounded">
                  <p className="text-sm font-medium text-green-900">Update Kurikulum Merdeka</p>
                  <p className="text-xs text-green-700 mt-1">
                    Format penilaian telah disesuaikan dengan standar terbaru.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Jadwal Penting
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                  <div>
                    <p className="text-sm font-medium">Batas Input Nilai PTS</p>
                    <p className="text-xs text-gray-600">Penilaian Tengah Semester</p>
                  </div>
                  <span className="text-sm font-semibold text-orange-600">15 Mar 2025</span>
                </div>
                <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                  <div>
                    <p className="text-sm font-medium">Batas Input Nilai PAS</p>
                    <p className="text-xs text-gray-600">Penilaian Akhir Semester</p>
                  </div>
                  <span className="text-sm font-semibold text-red-600">30 Jun 2025</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;