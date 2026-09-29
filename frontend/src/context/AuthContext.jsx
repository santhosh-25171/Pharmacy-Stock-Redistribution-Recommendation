import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
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

  const logout = useCallback(() => {
    localStorage.removeItem('pharmacy_token');
    setToken('');
    setUser(null);
    setError(null);
  }, []);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('pharmacy_token');
      if (storedToken) {
        try {
          const userData = await authService.getCurrentUser();
          setUser(userData);
          setToken(storedToken);
        } catch (err) {
          console.warn('[Auth] Stored token is invalid or expired. Session cleared.');
          logout();
        }
      } else {
        setUser(null);
        setToken('');
      }
      setLoading(false);
    };

    initAuth();

    // Listen for custom unauthorized events dispatched by API interceptors
    const handleUnauthorized = () => {
      console.warn('[Auth] Unauthorized 401 response detected. Redirecting to Login.');
      logout();
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, [logout]);

  const login = async (email, password) => {
    setError(null);
    try {
      const data = await authService.login(email, password);
      localStorage.setItem('pharmacy_token', data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      return data.user;
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Authentication failed. Please verify your credentials.';
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

export default AuthContext;
