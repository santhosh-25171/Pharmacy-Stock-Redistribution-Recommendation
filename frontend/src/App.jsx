import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
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
  const { user } = useAuth();
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

  const renderActivePage = () => {
    switch (currentTab) {
      case 'dashboard':
        return <Dashboard onNavigate={(tab) => setCurrentTab(tab)} />;
      case 'inventory':
        return <Inventory />;
      case 'recommendations':
        return <Recommendations />;
      case 'pharmacies':
        return <Pharmacies />;
      case 'analytics':
        return <Analytics />;
      case 'edgecases':
        return <EdgeCases />;
      case 'audit':
        return <AuditLogs />;
      case 'privacy':
        return <Privacy />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard onNavigate={(tab) => setCurrentTab(tab)} />;
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
