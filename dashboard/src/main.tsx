import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import { REFRESH_INTERVAL_SECONDS } from './config';
import './theme/dashboard.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchInterval: REFRESH_INTERVAL_SECONDS * 1000,
      refetchOnWindowFocus: false,
      staleTime: 30_000,
      retry: 1,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);
