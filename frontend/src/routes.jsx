import React from 'react';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import CV from './pages/CV';
import CVWriter from './pages/CVWriter';
import Jobs from './pages/Jobs';
import Chat from './pages/Chat';
import Applications from './pages/Applications';
import Alerts from './pages/Alerts';
import Settings from './pages/Settings';
import OAuthCallback from './pages/OAuthCallback';

const routes = [
  { path: '/login', element: <Login />, protected: false },
  { path: '/register', element: <Register />, protected: false },
  { path: '/oauth/callback', element: <OAuthCallback />, protected: false },
  { path: '/dashboard', element: <Dashboard />, protected: true },
  { path: '/profile', element: <Profile />, protected: true },
  { path: '/cv', element: <CV />, protected: true },
  { path: '/cv-writer', element: <CVWriter />, protected: true },
  { path: '/jobs', element: <Jobs />, protected: true },
  { path: '/chat', element: <Chat />, protected: true },
  { path: '/applications', element: <Applications />, protected: true },
  { path: '/alerts', element: <Alerts />, protected: true },
  { path: '/settings', element: <Settings />, protected: true },
];

export default routes;

