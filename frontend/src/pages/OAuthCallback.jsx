import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../hooks/useAuth';
import { Card } from '../components/Card';
import { Loader } from '../components/Loader';

/**
 * OAuth callback handler.
 * Expects the OAuth provider to redirect to /oauth/callback?provider=google&code=... or with tokens.
 * This page will attempt to exchange the code with the backend at /auth/oauth/callback
 * If the backend does not provide that endpoint, the UI will show a clear message.
 */

export default function OAuthCallback() {
  const [searchParams] = useSearchParams();
  const provider = searchParams.get('provider');
  const code = searchParams.get('code');
  const error = searchParams.get('error');
  const navigate = useNavigate();
  const { login } = useAuth();
  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState(null);

  useEffect(() => {
    let mounted = true;
    async function handle() {
      if (error) {
        setStatus('failed');
        setMessage(`Authentication cancelled or failed: ${error}`);
        return;
      }
      if (!provider) {
        setStatus('failed');
        setMessage('Missing provider parameter in callback URL.');
        return;
      }

      // If backend supports exchanging code:
      if (code) {
        setStatus('processing');
        try {
          // Attempt to call backend callback endpoint
          const res = await api.post(`/auth/oauth/callback?provider=${encodeURIComponent(provider)}`, { code });
          // Expect backend to return access_token or user object similar to /auth/login
          if (res?.access_token) {
            localStorage.setItem('avis_token', res.access_token);
            // attempt to fetch /auth/me via auth context
            try {
              await login({ email: '__oauth__', password: '__oauth__' }); // fallback: trigger auth.me refresh in context
            } catch {
              // ignore; auth context will refresh on next mount
            }
            if (mounted) {
              setStatus('success');
              setMessage('Authentication successful. Redirecting...');
              setTimeout(() => navigate('/dashboard'), 900);
            }
            return;
          } else {
            // If backend returns user object or other shape, still treat as success if token present
            setStatus('failed');
            setMessage('OAuth callback did not return an access token. Please check backend configuration.');
            return;
          }
        } catch (err) {
          setStatus('failed');
          setMessage(err?.message || 'OAuth exchange failed. Backend may not support this callback endpoint.');
          return;
        }
      }

      // If no code present, some providers may return tokens in fragment; frontend cannot read fragment after redirect from server.
      setStatus('failed');
      setMessage('No authorization code found in callback URL. Backend must support server-side exchange or return tokens.');
    }

    handle();
    return () => (mounted = false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="content" style={{ maxWidth: 720 }}>
      <Card title="OAuth callback">
        <div style={{ minHeight: 160, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12 }}>
          {status === 'processing' && (
            <>
              <Loader />
              <div className="small">Processing authentication with {provider}</div>
            </>
          )}
          {status === 'success' && <div style={{ color: 'green' }}>{message}</div>}
          {status === 'failed' && (
            <>
              <div role="alert" style={{ color: '#d14343' }}>{message}</div>
              <div className="small">If your backend does not support `/auth/oauth/callback`, configure server-side OAuth exchange or consult the backend team.</div>
            </>
          )}
        </div>
      </Card>
    </div>
  );
}
