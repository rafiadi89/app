import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import { Card, CardHeader, CardContent, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Users, UserCheck, School, BookOpen, Calendar, Settings } from 'lucide-react';
import { toast } from 'sonner';

const AdminPanel = () => {
  return (
    <Layout>
      <Routes>
        <Route index element={<AdminHome />} />
        <Route path="siswa" element={<StudentManagement />} />
        <Route path="guru" element={<TeacherManagement />} />
        <Route path="kelas" element={<ClassManagement />} />
        <Route path="mapel" element={<SubjectManagement />} />
        <Route path="tahun-ajaran" element={<AcademicYearManagement />} />
        <Route path="settings" element={<Settings />} />
      </Routes>
    </Layout>
  );
};

const AdminHome = () => {
  const adminModules = [
    {
      title: 'Kelola Siswa',
      description: 'Tambah, edit, dan kelola data siswa',
      icon: Users,
      color: 'bg-blue-500',
      href: '/admin/siswa'
    },
    {
      title: 'Kelola Guru', 
      description: 'Tambah, edit, dan kelola data guru',
      icon: UserCheck,
      color: 'bg-green-500',
      href: '/admin/guru'
    },
    {
      title: 'Kelola Kelas',
      description: 'Atur kelas dan wali kelas',
      icon: School,
      color: 'bg-purple-500', 
      href: '/admin/kelas'
    },
    {
      title: 'Mata Pelajaran',
      description: 'Kelola mata pelajaran dan guru pengampu',
      icon: BookOpen,
      color: 'bg-orange-500',
      href: '/admin/mapel'
    },
    {
      title: 'Tahun Ajaran',
      description: 'Atur tahun ajaran dan semester',
      icon: Calendar,
      color: 'bg-indigo-500',
      href: '/admin/tahun-ajaran'
    },
    {
      title: 'Pengaturan',
      description: 'Konfigurasi sistem dan backup data',
      icon: Settings,
      color: 'bg-gray-500',
      href: '/admin/settings'
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Panel Administrator</h1>
        <p className="text-gray-600">Kelola semua aspek sistem E-Rapor SMK</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {adminModules.map((module, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className={`w-12 h-12 rounded-xl ${module.color} flex items-center justify-center`}>
                  <module.icon className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">{module.title}</h3>
                  <p className="text-sm text-gray-600 mb-4">{module.description}</p>
                  <Button
                    size="sm"
                    onClick={() => toast.info(`Fitur ${module.title} segera hadir!`)}
                  >
                    Buka
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

const StudentManagement = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold text-gray-900">Kelola Siswa</h1>
    <Card>
      <CardContent className="p-8 text-center">
        <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Fitur Kelola Siswa</h3>
        <p className="text-gray-600 mb-4">
          Fitur CRUD siswa, upload foto, dan manajemen data siswa lengkap akan segera tersedia.
        </p>
        <Button onClick={() => toast.info('Fitur ini sedang dalam pengembangan')}>
          Segera Hadir
        </Button>
      </CardContent>
    </Card>
  </div>
);

const TeacherManagement = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold text-gray-900">Kelola Guru</h1>
    <Card>
      <CardContent className="p-8 text-center">
        <UserCheck className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Fitur Kelola Guru</h3>
        <p className="text-gray-600 mb-4">
          Fitur CRUD guru, NUPTK, dan assignment mata pelajaran akan segera tersedia.
        </p>
        <Button onClick={() => toast.info('Fitur ini sedang dalam pengembangan')}>
          Segera Hadir
        </Button>
      </CardContent>
    </Card>
  </div>
);

const ClassManagement = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold text-gray-900">Kelola Kelas</h1>
    <Card>
      <CardContent className="p-8 text-center">
        <School className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Fitur Kelola Kelas</h3>
        <p className="text-gray-600 mb-4">
          Fitur CRUD kelas, assignment wali kelas, dan organisasi siswa akan segera tersedia.
        </p>
        <Button onClick={() => toast.info('Fitur ini sedang dalam pengembangan')}>
          Segera Hadir
        </Button>
      </CardContent>
    </Card>
  </div>
);

const SubjectManagement = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold text-gray-900">Kelola Mata Pelajaran</h1>
    <Card>
      <CardContent className="p-8 text-center">
        <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Fitur Kelola Mata Pelajaran</h3>
        <p className="text-gray-600 mb-4">
          Fitur CRUD mata pelajaran, assignment guru pengampu akan segera tersedia.
        </p>
        <Button onClick={() => toast.info('Fitur ini sedang dalam pengembangan')}>
          Segera Hadir
        </Button>
      </CardContent>
    </Card>
  </div>
);

const AcademicYearManagement = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold text-gray-900">Kelola Tahun Ajaran</h1>
    <Card>
      <CardContent className="p-8 text-center">
        <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Fitur Tahun Ajaran</h3>
        <p className="text-gray-600 mb-4">
          Fitur CRUD tahun ajaran, semester, dan naik kelas otomatis akan segera tersedia.
        </p>
        <Button onClick={() => toast.info('Fitur ini sedang dalam pengembangan')}>
          Segera Hadir
        </Button>
      </CardContent>
    </Card>
  </div>
);

export default AdminPanel;