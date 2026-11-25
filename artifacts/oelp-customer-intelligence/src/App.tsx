import { lazy, Suspense, useMemo } from 'react';
import { BrowserRouter, NavLink, Route, Routes, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  Activity, BarChart3, BookOpen, History, LayoutDashboard, UploadCloud, UserRoundSearch, Users, Wallet,
} from 'lucide-react';
import {
  getGetApiHealthQueryKey, getHealthCheckQueryKey, useGetApiHealth, useHealthCheck,
} from '@workspace/api-client-react';
import { Loading, PageHeading } from './components/app-shared';
import './index.css';

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000, retry: 1 } } });
const OverviewPage = lazy(() => import('./pages/OverviewPage'));
const SegmentsPage = lazy(() => import('./pages/SegmentsPage'));
const IntelligencePage = lazy(() => import('./pages/IntelligencePage'));
const BehaviorPage = lazy(() => import('./BehaviorPage'));
const ForecastingPage = lazy(() => import('./pages/ForecastingPage'));
const UploadPage = lazy(() => import('./pages/UploadPage'));
const PerformancePage = lazy(() => import('./pages/PerformancePage'));
const RevenueExposurePage = lazy(() => import('./RevenueExposurePage'));
const TrajectoryPage = lazy(() => import('./TrajectoryPage'));
const ResearchPage = lazy(() => import('./ResearchPage'));

function AppShell() {
  const location = useLocation();
  const health = useHealthCheck({ query: { queryKey: getHealthCheckQueryKey(), refetchInterval: 60_000 } });
  const previewHealth = useGetApiHealth({ query: { queryKey: getGetApiHealthQueryKey(), refetchInterval: 60_000 } });
  const title = useMemo(() => {
    const titles: Record<string, string> = {
      '/': 'Business overview',
      '/research': 'Research overview',
      '/segments': 'Customer segments',
      '/intelligence': 'Customer intelligence',
      '/behavior': 'Behavior indicators',
      '/forecasting': 'Forecast workspace',
      '/upload': 'Upload analysis',
      '/model-performance': 'Model performance',
      '/revenue-exposure': 'Revenue & retention',
      '/trajectories': 'Trajectory explorer',
    };
    return titles[location.pathname] ?? 'Workspace';
  }, [location.pathname]);
  const links = [
    { to: '/', label: 'Business overview', icon: LayoutDashboard },
    { to: '/research', label: 'Research overview', icon: BookOpen },
    { to: '/segments', label: 'Segments', icon: Users },
    { to: '/intelligence', label: 'Customer intelligence', icon: UserRoundSearch },
    { to: '/behavior', label: 'Behavior indicators', icon: History },
    { to: '/forecasting', label: 'Forecasting', icon: Activity },
    { to: '/upload', label: 'Upload analysis', icon: UploadCloud },
    { to: '/model-performance', label: 'Model performance', icon: BarChart3 },
    { to: '/revenue-exposure', label: 'Revenue & retention', icon: Wallet },
    { to: '/trajectories', label: 'Trajectory explorer', icon: Activity },
  ];
  const connected = health.isSuccess || previewHealth.isSuccess;
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark">O</div><div><div className="brand-name">OELP Intelligence</div><div className="brand-sub">Customer retention</div></div></div>
      <nav aria-label="Primary navigation"><div className="nav-label">Workspace</div><div className="nav-list">{links.map(({ to, label, icon: Icon }) => <NavLink to={to} end={to === '/'} key={to} className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`} data-testid={`link-${to === '/' ? 'overview' : to.slice(1)}`}><Icon /><span>{label}</span></NavLink>)}</div></nav>
      <div className="side-foot"><strong>HISTORICAL DATASET</strong><br />Saved notebook evaluations<br />No live business connection</div>
    </aside>
    <main className="main-area">
      <header className="topbar"><div className="crumb">OELP / {title}</div><div className="top-right"><div className="status-pill"><span className="status-dot" style={{ background: connected ? '#4b9c79' : '#c7a15e' }} />{connected ? 'API connected' : health.isLoading || previewHealth.isLoading ? 'Checking API' : 'API unavailable'}</div><div className="top-date">SAVED MODEL WORKSPACE</div></div></header>
      <Suspense fallback={<div className="content"><Loading rows={2} /></div>}>
        <Routes>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/research" element={<ResearchPage />} />
          <Route path="/segments" element={<SegmentsPage />} />
          <Route path="/intelligence" element={<IntelligencePage />} />
          <Route path="/behavior" element={<BehaviorPage />} />
          <Route path="/forecasting" element={<ForecastingPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/model-performance" element={<PerformancePage />} />
          <Route path="/revenue-exposure" element={<RevenueExposurePage />} />
          <Route path="/trajectories" element={<TrajectoryPage />} />
          <Route path="*" element={<div className="content"><PageHeading eyebrow="Not found" title="This workspace page is unavailable" description="Choose a destination from the workspace navigation." /><NavLink className="button" to="/">Return to overview</NavLink></div>} />
        </Routes>
      </Suspense>
    </main>
  </div>;
}

export default function App() {
  return <QueryClientProvider client={queryClient}><BrowserRouter><AppShell /></BrowserRouter></QueryClientProvider>;
}
