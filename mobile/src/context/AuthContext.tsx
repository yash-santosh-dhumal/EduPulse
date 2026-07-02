import React, { createContext, useContext, useEffect, useState } from 'react';
import { getAuthToken, setAuthToken, clearAuthToken, apiClient } from '../api/client';

export type UserRole = 'admin' | 'teacher' | 'student';

export interface User {
  id: number;
  email: string;
  name: string;
  role: UserRole;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (token: string, user: User) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  login: async () => {},
  logout: async () => {},
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadToken = async () => {
      try {
        const token = await getAuthToken();
        if (token) {
          // Attempt to fetch current user profile to validate token
          const profile = await apiClient.get<User>('/api/v1/auth/me');
          setUser(profile);
        }
      } catch (e) {
        console.log('Token invalid or expired', e);
        await clearAuthToken();
      } finally {
        setIsLoading(false);
      }
    };
    loadToken();
  }, []);

  const login = async (token: string, userData: User) => {
    await setAuthToken(token);
    setUser(userData);
  };

  const logout = async () => {
    await clearAuthToken();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
