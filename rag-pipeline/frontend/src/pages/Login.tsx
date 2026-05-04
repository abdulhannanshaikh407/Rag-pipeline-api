import { useState } from 'react';
import { login, register } from '../lib/api';
import { Sparkles } from 'lucide-react';

interface LoginProps {
  onSuccess: () => void;
}

export default function Login({ onSuccess }: LoginProps) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError('');
    setLoading(true);
    try {
      if (mode === 'register') {
        await register(username, email, password);
      }
      await login(username, password);
      onSuccess();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#080d1a] items-center justify-center">
      <div className="bg-[#0f1629]/70 backdrop-blur-md rounded-2xl p-10 w-full max-w-md border border-white/10">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#6C63FF] to-[#3622ca] flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-white font-bold text-lg">Aether Engine</h1>
            <p className="text-slate-400 text-xs">RAG Pipeline Interface</p>
          </div>
        </div>

        <div className="flex gap-2 mb-6">
          {(['login', 'register'] as const).map(m => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`flex-1 py-2 rounded-lg text-xs font-bold uppercase tracking-widest transition-all ${
                mode === m ? 'bg-[#6C63FF] text-white' : 'bg-white/5 text-slate-400 hover:bg-white/10'
              }`}
            >
              {m}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          <input
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white text-sm placeholder:text-slate-500 focus:outline-none focus:border-[#6C63FF]/50"
            placeholder="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
          />
          {mode === 'register' && (
            <input
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white text-sm placeholder:text-slate-500 focus:outline-none focus:border-[#6C63FF]/50"
              placeholder="Email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
          )}
          <input
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white text-sm placeholder:text-slate-500 focus:outline-none focus:border-[#6C63FF]/50"
            placeholder="Password"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
          />
        </div>

        {error && <p className="text-red-400 text-xs mt-3">{error}</p>}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full mt-6 py-3 bg-[#6C63FF] text-white rounded-xl font-bold text-sm hover:shadow-[0_0_20px_rgba(108,99,255,0.4)] transition-all disabled:opacity-50"
        >
          {loading ? 'Connecting...' : mode === 'login' ? 'Access System' : 'Initialize Account'}
        </button>
      </div>
    </div>
  );
}
