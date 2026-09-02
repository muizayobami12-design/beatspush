'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/authStore';

export default function DebugPage() {
  const authStore = useAuthStore();
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (msg: string) => {
    console.log('[DEBUG]', msg);
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${msg}`]);
  };

  useEffect(() => {
    addLog('Debug page loaded');
    
    if (typeof window !== 'undefined') {
      addLog(`localStorage auth_token: ${localStorage.getItem('auth_token') ? 'SET' : 'MISSING'}`);
      addLog(`localStorage user: ${localStorage.getItem('user') ? 'SET' : 'MISSING'}`);
      addLog(`Cookies: ${document.cookie || 'EMPTY'}`);
    }

    addLog(`Store isAuthenticated: ${authStore.isAuthenticated}`);
    addLog(`Store token: ${authStore.token ? 'SET' : 'MISSING'}`);
    addLog(`Store user: ${authStore.user ? 'SET' : 'MISSING'}`);
  }, [authStore]);

  const handleTestLogin = async () => {
    addLog('Starting test login...');
    
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'testuser@example.com',
          password: 'TestPassword123',
        }),
      });

      addLog(`API response status: ${response.status}`);

      const data = await response.json();
      addLog(`API returned user: ${data.user?.email}`);

      const token = data.token || data.access_token;
      addLog(`Token extracted: ${token ? token.substring(0, 20) + '...' : 'MISSING'}`);

      if (token && data.user) {
        addLog('Storing in localStorage...');
        localStorage.setItem('auth_token', token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        addLog('Calling authStore.login()...');
        authStore.login(data.user, token);
        
        addLog('Waiting 500ms...');
        await new Promise(r => setTimeout(r, 500));
        
        addLog(`After login - Store token: ${authStore.token ? 'SET' : 'MISSING'}`);
        addLog(`After login - localStorage token: ${localStorage.getItem('auth_token') ? 'SET' : 'MISSING'}`);
      }
    } catch (err: any) {
      addLog(`Error: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-foreground">Debug Page</h1>

        <div className="bg-card rounded-lg border border-border p-6 mb-6 space-y-4">
          <div>
            <h2 className="text-lg font-bold text-foreground mb-3">Auth Store State</h2>
            <pre className="bg-muted p-3 rounded text-xs overflow-auto text-foreground max-h-40">
              {JSON.stringify({
                isAuthenticated: authStore.isAuthenticated,
                token: authStore.token ? authStore.token.substring(0, 20) + '...' : 'MISSING',
                user: authStore.user?.email || 'MISSING',
              }, null, 2)}
            </pre>
          </div>

          <button
            onClick={handleTestLogin}
            className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg"
          >
            Test Login
          </button>
        </div>

        <div className="bg-card rounded-lg border border-border p-6">
          <h2 className="text-lg font-bold text-foreground mb-3">Logs</h2>
          <pre className="bg-muted p-3 rounded text-xs overflow-auto text-foreground max-h-64 space-y-1">
            {logs.map((log, i) => (
              <div key={i}>{log}</div>
            ))}
          </pre>
        </div>

        <div className="mt-6 text-center">
          <a href="/dashboard" className="text-primary hover:underline">
            Try Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}
