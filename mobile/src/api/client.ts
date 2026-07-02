import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

// Use 10.0.2.2 for Android emulator, localhost for iOS/web
const DEV_URL = Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000';
export const API_BASE = process.env.EXPO_PUBLIC_API_URL || DEV_URL;

export const setAuthToken = async (token: string) => {
  await SecureStore.setItemAsync('auth_token', token);
};

export const getAuthToken = async (): Promise<string | null> => {
  return await SecureStore.getItemAsync('auth_token');
};

export const clearAuthToken = async () => {
  await SecureStore.deleteItemAsync('auth_token');
};

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, data: any) {
    super(data?.detail || 'API Error');
    this.status = status;
    this.data = data;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  
  const token = await getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData = {};
    try {
      errorData = await response.json();
    } catch {
      // Ignore if not JSON
    }
    
    // AuthContext will need a way to intercept 401s, but for now we just throw
    throw new ApiError(response.status, errorData);
  }

  // Handle empty responses (like 204 No Content)
  const text = await response.text();
  return text ? JSON.parse(text) : ({} as T);
}

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'GET' }),
  post: <T>(endpoint: string, data?: any, options?: RequestInit) => request<T>(endpoint, {
    ...options,
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  }),
  patch: <T>(endpoint: string, data?: any, options?: RequestInit) => request<T>(endpoint, {
    ...options,
    method: 'PATCH',
    body: data ? JSON.stringify(data) : undefined,
  }),
  delete: <T>(endpoint: string, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'DELETE' }),
};
