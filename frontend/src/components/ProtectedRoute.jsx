import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { Navigate } from 'react-router-dom';

export function ProtectedRoute({ children }) {
  const { user, loadingAuth } = useAuth();
  if (loadingAuth) return <div className="center">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}
