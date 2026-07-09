import React, { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, Lock, User, AtSign, Sparkles, ArrowRight, Eye, EyeOff, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuthStore } from '@/store/auth-store';
import toast from 'react-hot-toast';

const particles = Array.from({ length: 35 }, (_, i) => ({
  id: i,
  x: Math.random() * 100,
  y: Math.random() * 100,
  size: Math.random() * 3 + 1,
  duration: Math.random() * 10 + 8,
  delay: Math.random() * 5,
}));

const passwordRequirements = [
  { label: 'At least 8 characters', test: (p: string) => p.length >= 8 },
  { label: 'Contains uppercase letter', test: (p: string) => /[A-Z]/.test(p) },
  { label: 'Contains a number', test: (p: string) => /[0-9]/.test(p) },
];

const RegisterPage: React.FC = () => {
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { register, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const gridLines = useMemo(() => Array.from({ length: 20 }, (_, i) => i), []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !username || !email || !password || !confirmPassword) {
      toast.error('Please fill in all fields');
      return;
    }
    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    if (password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    try {
      await register({ full_name: fullName, username, email, password });
      toast.success('Account created successfully!');
      navigate('/dashboard');
    } catch {
      toast.error('Registration failed. Please try again.');
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-950">
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-indigo-950/50 to-slate-950" />
        <div
          className="absolute inset-0 animate-gradient-shift opacity-60"
          style={{
            background:
              'radial-gradient(ellipse at 80% 50%, rgba(99,102,241,0.15) 0%, transparent 60%), radial-gradient(ellipse at 20% 80%, rgba(59,130,246,0.12) 0%, transparent 60%), radial-gradient(ellipse at 50% 20%, rgba(139,92,246,0.1) 0%, transparent 60%)',
            backgroundSize: '200% 200%',
          }}
        />
      </div>

      {/* Grid */}
      <div className="absolute inset-0 overflow-hidden opacity-[0.04]">
        {gridLines.map((i) => (
          <React.Fragment key={i}>
            <div className="absolute left-0 right-0 h-px bg-white" style={{ top: `${(i + 1) * 5}%` }} />
            <div className="absolute top-0 bottom-0 w-px bg-white" style={{ left: `${(i + 1) * 5}%` }} />
          </React.Fragment>
        ))}
      </div>

      {/* Particles */}
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full bg-blue-400/30"
          style={{ width: p.size, height: p.size, left: `${p.x}%`, top: `${p.y}%` }}
          animate={{ y: [0, -25, 0], x: [0, 10, -10, 0], opacity: [0.2, 0.5, 0.2] }}
          transition={{ duration: p.duration, delay: p.delay, repeat: Infinity, ease: 'easeInOut' }}
        />
      ))}

      {/* Registration Card */}
      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="relative z-10 w-full max-w-md px-4 py-8"
      >
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-8 shadow-2xl shadow-indigo-500/5 backdrop-blur-xl">
          {/* Logo */}
          <motion.div
            className="mb-8 flex flex-col items-center"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <motion.div
              className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-blue-600 shadow-xl shadow-indigo-500/30"
              whileHover={{ scale: 1.05, rotate: -5 }}
              transition={{ type: 'spring', stiffness: 400, damping: 15 }}
            >
              <Sparkles className="h-7 w-7 text-white" />
            </motion.div>
            <h1 className="bg-gradient-to-r from-white to-white/80 bg-clip-text text-2xl font-bold text-transparent">
              Create Account
            </h1>
            <p className="mt-1 text-sm text-slate-400">
              Join ResearchMind AI for free
            </p>
          </motion.div>

          <motion.form
            onSubmit={handleSubmit}
            className="space-y-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <Input
              label="Full Name"
              type="text"
              placeholder="Dr. Jane Smith"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              icon={<User className="h-4 w-4" />}
              className="border-white/10 bg-white/[0.04] text-white placeholder:text-slate-500 hover:border-indigo-500/30 focus:border-indigo-500 focus:ring-indigo-500/20"
            />

            <Input
              label="Username"
              type="text"
              placeholder="janesmith"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              icon={<AtSign className="h-4 w-4" />}
              className="border-white/10 bg-white/[0.04] text-white placeholder:text-slate-500 hover:border-indigo-500/30 focus:border-indigo-500 focus:ring-indigo-500/20"
            />

            <Input
              label="Email"
              type="email"
              placeholder="jane@university.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              icon={<Mail className="h-4 w-4" />}
              className="border-white/10 bg-white/[0.04] text-white placeholder:text-slate-500 hover:border-indigo-500/30 focus:border-indigo-500 focus:ring-indigo-500/20"
            />

            <div className="relative">
              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Create a strong password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                icon={<Lock className="h-4 w-4" />}
                className="border-white/10 bg-white/[0.04] text-white placeholder:text-slate-500 hover:border-indigo-500/30 focus:border-indigo-500 focus:ring-indigo-500/20 pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-[38px] text-slate-500 hover:text-slate-300 transition-colors cursor-pointer"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>

            {/* Password strength */}
            {password.length > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="space-y-1.5 overflow-hidden"
              >
                {passwordRequirements.map((req) => (
                  <div key={req.label} className="flex items-center gap-2">
                    <CheckCircle2
                      className={`h-3.5 w-3.5 transition-colors ${
                        req.test(password) ? 'text-emerald-400' : 'text-slate-600'
                      }`}
                    />
                    <span
                      className={`text-xs transition-colors ${
                        req.test(password) ? 'text-emerald-400' : 'text-slate-500'
                      }`}
                    >
                      {req.label}
                    </span>
                  </div>
                ))}
              </motion.div>
            )}

            <Input
              label="Confirm Password"
              type="password"
              placeholder="Confirm your password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              icon={<Lock className="h-4 w-4" />}
              error={confirmPassword && password !== confirmPassword ? 'Passwords do not match' : undefined}
              className="border-white/10 bg-white/[0.04] text-white placeholder:text-slate-500 hover:border-indigo-500/30 focus:border-indigo-500 focus:ring-indigo-500/20"
            />

            <Button
              type="submit"
              className="w-full h-11 bg-gradient-to-r from-indigo-500 to-blue-600 text-white font-semibold shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:from-indigo-600 hover:to-blue-700 transition-all mt-2"
              isLoading={isLoading}
            >
              Create Account
              <ArrowRight className="h-4 w-4" />
            </Button>
          </motion.form>

          <motion.p
            className="mt-6 text-center text-sm text-slate-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-indigo-400 hover:text-indigo-300 transition-colors">
              Sign in
            </Link>
          </motion.p>
        </div>

        <motion.p
          className="mt-6 text-center text-xs text-slate-600"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
        >
          By creating an account, you agree to our Terms of Service
        </motion.p>
      </motion.div>
    </div>
  );
};

export default RegisterPage;
