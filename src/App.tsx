import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DashboardLayout } from './components/layout';
import { Dashboard } from './pages/Dashboard';
import { PipelinesPage } from './pages/Pipelines';
import { ExecutionsPage } from './pages/Executions';
import { AIInsightsPage } from './pages/AIInsights';
import { LogsPage } from './pages/Logs';
import { AlertsPage } from './pages/Alerts';
import { Settings } from './pages/Settings';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<DashboardLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="pipelines" element={<PipelinesPage />} />
            <Route path="executions" element={<ExecutionsPage />} />
            <Route path="ai-insights" element={<AIInsightsPage />} />
            <Route path="logs" element={<LogsPage />} />
            <Route path="alerts" element={<AlertsPage />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
