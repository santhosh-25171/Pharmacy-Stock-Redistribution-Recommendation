import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext();

export const DEMO_ACCOUNTS = [
  { email: 'admin@pharmacy.io', role: 'ADMIN', name: 'System Administrator', label: 'Admin (All Access)' },
  { email: 'manager@pharmacy.io', role: 'MANAGER', name: 'Regional Supply Chain Manager', label: 'Regional Manager' },
  { email: 'pharmacist@pharmacy.io', role: 'PHARMACIST', name: 'Senior Pharmacist (Central Hub)', label: 'Pharmacist (Hub PHARM-001)' },
  { email: 'pharmacist2@pharmacy.io', role: 'PHARMACIST', name: 'Duty Pharmacist (Indiranagar)', label: 'Pharmacist (Indiranagar PHARM-002)' }
];

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('pharmacy_token') || '');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('pharmacy_token');
      if (storedToken) {
        try {
          const userData = await authService.getCurrentUser();
          setUser(userData);
        } catch (err) {
          console.warn('[Auth] Token expired or invalid, logging in as default Admin');
          await loginAsDemo('admin@pharmacy.io');
        }
      } else {
        // Automatically login as Admin by default for immediate demo readiness
        await loginAsDemo('admin@pharmacy.io');
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    setError(null);
    try {
      const data = await authService.login(email, password);
      localStorage.setItem('pharmacy_token', data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      return data.user;
    } catch (err) {
      const msg = err.response?.data?.detail || 'Authentication failed';
      setError(msg);
      throw new Error(msg);
    }
  };

  const loginAsDemo = async (email) => {
    const defaultPassword = email.startsWith('admin')
      ? 'Admin@123'
      : (email.startsWith('manager') ? 'Manager@123' : 'Pharmacist@123');
    return login(email, defaultPassword);
  };

  const logout = () => {
    localStorage.removeItem('pharmacy_token');
    setToken('');
    setUser(null);
  };

  const hasRole = (allowedRoles) => {
    if (!user) return false;
    if (typeof allowedRoles === 'string') return user.role === allowedRoles;
    return allowedRoles.includes(user.role);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        error,
        login,
        loginAsDemo,
        logout,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
