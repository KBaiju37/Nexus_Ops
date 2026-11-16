import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import ApplicationsPage from './pages/ApplicationsPage';
import DeploymentsPage from './pages/DeploymentsPage';
import IncidentsPage from './pages/IncidentsPage';
import MonitoringPage from './pages/MonitoringPage';
import AboutPage from './pages/AboutPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/applications" element={<ApplicationsPage />} />
        <Route path="/deployments" element={<DeploymentsPage />} />
        <Route path="/incidents" element={<IncidentsPage />} />
        <Route path="/monitoring" element={<MonitoringPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
