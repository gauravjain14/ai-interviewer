'use client';

import { useState } from 'react';

const socialProviders = [
  { id: 'instagram', label: 'Continue with Instagram' },
  { id: 'x', label: 'Continue with X' },
];

export function AuthPanel() {
  const [mode, setMode] = useState<'login' | 'signup'>('signup');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(`/api/auth/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const result = await response.json();
      setMessage(result.message ?? 'Request completed.');
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleSocial = async (provider: string) => {
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch('/api/auth/social', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider }),
      });
      const result = await response.json();
      setMessage(result.message ?? 'Redirecting to provider...');
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card-shadow rounded-2xl border border-border bg-white p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted">Welcome</p>
          <h3 className="text-xl font-semibold">Sign up or log in</h3>
        </div>
        <div className="flex items-center gap-2 rounded-full bg-surface px-3 py-1 text-xs font-semibold text-accent">
          <button
            className={`rounded-full px-3 py-1 ${mode === 'signup' ? 'bg-accent text-white' : ''}`}
            type="button"
            onClick={() => setMode('signup')}
          >
            Sign up
          </button>
          <button
            className={`rounded-full px-3 py-1 ${mode === 'login' ? 'bg-accent text-white' : ''}`}
            type="button"
            onClick={() => setMode('login')}
          >
            Log in
          </button>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        <div className="space-y-1">
          <label className="text-sm font-semibold" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            placeholder="you@example.com"
          />
        </div>
        <div className="space-y-1">
          <label className="text-sm font-semibold" htmlFor="password">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            placeholder="Create a password"
          />
        </div>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={loading}
          className="w-full rounded-xl bg-accent px-4 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 disabled:opacity-50"
        >
          {loading ? 'Working...' : mode === 'signup' ? 'Create account' : 'Log in'}
        </button>

        <div className="flex items-center gap-3 py-2 text-xs text-muted">
          <div className="h-px flex-1 bg-border" />
          or
          <div className="h-px flex-1 bg-border" />
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          {socialProviders.map((provider) => (
            <button
              key={provider.id}
              type="button"
              onClick={() => handleSocial(provider.id)}
              disabled={loading}
              className="flex items-center justify-center gap-2 rounded-xl border border-border bg-surface px-3 py-2 text-sm font-semibold text-primary transition hover:border-accent/40 disabled:opacity-50"
            >
              <span>{provider.label}</span>
            </button>
          ))}
        </div>

        {message && <p className="text-sm text-accent">{message}</p>}
      </div>
    </section>
  );
}
