// src/auth/useAxiosAuth.ts
import { useKeycloak } from '@react-keycloak/web';
import { useEffect } from 'react';
import axiosInstance from '../api/axiosInstance';

export const useAxiosAuth = () => {
  const { keycloak } = useKeycloak();

  useEffect(() => {
    // Add a request interceptor
    const interceptor = axiosInstance.interceptors.request.use(
      async (config) => {
        if (keycloak?.token) {
          config.headers = config.headers ?? {};
          config.headers['Authorization'] = `Bearer ${keycloak.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Cleanup: remove the interceptor when component unmounts or token changes
    return () => {
      axiosInstance.interceptors.request.eject(interceptor);
    };
  }, [keycloak?.token]);
};