import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { Login } from './pages/Login';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Dashboard } from './pages/Dashboard';
import { Inventory } from './pages/Inventory';
import { Recommendations } from './pages/Recommendations';
import { Pharmacies } from './pages/Pharmacies';
import { Analytics } from './pages/Analytics';
import { AuditLogs } from './pages/AuditLogs';
import { EdgeCases } from './pages/EdgeCases';
import { Privacy } from './pages/Privacy';
import { Settings } from './pages/Settings';
import { recommendationService, inventoryService } from './services/api';

const AppContent = () => {
  const { user, loading } = useAuth();
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [counts, setCounts] = useState({ pendingRecs: null, inventoryCount: null });

  const fetchBadgeCounts = async () => {
    try {
      const [recs, inv] = await Promise.all([
        recommendationService.getRecommendations({ status: 'PENDING' }),
        inventoryService.getInventory({ limit: 1 }),
      ]);
      setCounts({
        pendingRecs: recs.length > 0 ? recs.length : null,
        inventoryCount: '5,000+',
      });
    } catch (err) {
      // Background count fetch error fallback
    }
  };

  useEffect(() => {
    if (user) {
      fetchBadgeCounts();
    }
  }, [user, currentTab]);

  // Loading state while verifying stored session token
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-400 gap-3">
        <div className="w-9 h-9 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-xs font-semibold tracking-wide text-slate-300">Initializing PharmaShift session...</p>
      </div>
    );
  }

  // CRITICAL REQUIREMENT: If not authenticated, render Login Page exclusively
  if (!user) {
    return <Login />;
  }

  const renderActivePage = () => {
    switch (currentTab) {
      case 'dashboard':
        return (
          <ErrorBoundary sectionName="Dashboard">
            <Dashboard onNavigate={(tab) => setCurrentTab(tab)} />
          </ErrorBoundary>
        );
      case 'inventory':
        return (
          <ErrorBoundary sectionName="Inventory Monitor">
            <Inventory />
          </ErrorBoundary>
        );
      case 'recommendations':
        return (
          <ErrorBoundary sectionName="Transfer Recommendations">
            <Recommendations />
          </ErrorBoundary>
        );
      case 'pharmacies':
        return (
          <ErrorBoundary sectionName="Pharmacy Network">
            <Pharmacies />
          </ErrorBoundary>
        );
      case 'analytics':
        return (
          <ErrorBoundary sectionName="Analytics & Simulation Benchmarks">
            <Analytics />
          </ErrorBoundary>
        );
      case 'edgecases':
        return (
          <ErrorBoundary sectionName="Edge Cases Sandbox">
            <EdgeCases />
          </ErrorBoundary>
        );
      case 'audit':
        return (
          <ErrorBoundary sectionName="Audit Trail">
            <AuditLogs />
          </ErrorBoundary>
        );
      case 'privacy':
        return (
          <ErrorBoundary sectionName="Privacy & Consent">
            <Privacy />
          </ErrorBoundary>
        );
      case 'settings':
        return (
          <ErrorBoundary sectionName="Settings">
            <Settings />
          </ErrorBoundary>
        );
      default:
        return (
          <ErrorBoundary sectionName="Dashboard">
            <Dashboard onNavigate={(tab) => setCurrentTab(tab)} />
          </ErrorBoundary>
        );
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <Navbar onOpenPrivacy={() => setCurrentTab('privacy')} />

      {/* Main App Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar Navigation */}
        <Sidebar
          currentTab={currentTab}
          onSelectTab={(tab) => setCurrentTab(tab)}
          counts={counts}
        />

        {/* Dynamic Page Container */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="max-w-7xl mx-auto">
            {renderActivePage()}
          </div>
        </main>
      </div>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
