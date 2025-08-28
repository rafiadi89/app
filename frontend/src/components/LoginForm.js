import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../App';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Eye, EyeOff, GraduationCap, Users, BookOpen, BarChart3 } from 'lucide-react';
import { toast } from 'sonner';

const LoginForm = () => {
  const { user, login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Redirect if already logged in
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      toast.success('Login berhasil! Selamat datang di E-Rapor SMK');
    } else {
      setError(result.error);
      toast.error('Login gagal. Periksa email dan password Anda.');
    }
    
    setLoading(false);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // Demo accounts for testing
  const demoAccounts = [
    { role: 'Admin', email: 'admin@smk.sch.id', password: 'admin123' },
    { role: 'Guru Mapel', email: 'guru@smk.sch.id', password: 'guru123' },
    { role: 'Wali Kelas', email: 'wali@smk.sch.id', password: 'wali123' }
  ];

  const fillDemoAccount = (account) => {
    setFormData({
      email: account.email,
      password: account.password
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-8 items-center">
        
        {/* Left side - Branding */}
        <div className="hidden lg:block space-y-8 animate-fadeIn">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-600 rounded-2xl mb-6">
              <GraduationCap className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              E-Rapor SMK
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Sistem Manajemen Rapor Digital untuk SMK Kurikulum Merdeka
            </p>
          </div>

          {/* Features showcase */}
          <div className="grid grid-cols-2 gap-6">
            <div className="text-center p-6 rounded-xl bg-white/50 backdrop-blur-sm border border-white/20">
              <Users className="w-8 h-8 text-blue-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-1">Multi Role</h3>
              <p className="text-sm text-gray-600">Admin, Guru, Wali Kelas</p>
            </div>
            <div className="text-center p-6 rounded-xl bg-white/50 backdrop-blur-sm border border-white/20">
              <BookOpen className="w-8 h-8 text-green-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-1">Kurikulum Merdeka</h3>
              <p className="text-sm text-gray-600">Penilaian P5, PKL, Ekstra</p>
            </div>
            <div className="text-center p-6 rounded-xl bg-white/50 backdrop-blur-sm border border-white/20">
              <BarChart3 className="w-8 h-8 text-purple-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-1">Analitik</h3>
              <p className="text-sm text-gray-600">Dashboard & Laporan</p>
            </div>
            <div className="text-center p-6 rounded-xl bg-white/50 backdrop-blur-sm border border-white/20">
              <GraduationCap className="w-8 h-8 text-indigo-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-1">Cetak Rapor</h3>
              <p className="text-sm text-gray-600">Format PDF Resmi</p>
            </div>
          </div>
        </div>

        {/* Right side - Login Form */}
        <div className="animate-slideIn">
          <Card className="w-full max-w-md mx-auto card-shadow-lg">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl font-bold text-gray-900">
                Masuk ke Sistem
              </CardTitle>
              <CardDescription className="text-gray-600">
                Silakan masuk dengan akun Anda
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-6">
              {error && (
                <Alert className="border-red-200 bg-red-50">
                  <AlertDescription className="text-red-700">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="nama@smk.sch.id"
                    required
                    className="input-focus"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="Masukkan password"
                      required
                      className="input-focus pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full bg-blue-600 hover:bg-blue-700 btn-focus"
                  disabled={loading}
                >
                  {loading ? (
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 loading-spinner"></div>
                      Memproses...
                    </div>
                  ) : (
                    'Masuk'
                  )}
                </Button>
              </form>

              {/* Demo accounts for testing */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <p className="text-sm text-gray-600 mb-3 text-center">
                  Akun Demo untuk Testing:
                </p>
                <div className="grid gap-2">
                  {demoAccounts.map((account, index) => (
                    <button
                      key={index}
                      onClick={() => fillDemoAccount(account)}
                      className="text-left p-3 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                    >
                      <div className="font-medium text-gray-900">{account.role}</div>
                      <div className="text-gray-600">{account.email}</div>
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;