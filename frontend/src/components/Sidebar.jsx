import React from 'react';
import {
  LayoutDashboard,
  Boxes,
  Sparkles,
  Building2,
  BarChart3,
  History,
  ShieldAlert,
  Lock,
  Settings,
  Flame,
  CheckCircle,
  LogOut,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Sidebar = ({ currentTab, onSelectTab, counts = {} }) => {
  const { user, hasRole, logout } = useAuth();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, badge: null },
    { id: 'inventory', label: 'Inventory Monitor', icon: Boxes, badge: counts.inventoryCount },
    { id: 'recommendations', label: 'Recommendations', icon: Sparkles, badge: counts.pendingRecs, highlight: true },
    { id: 'pharmacies', label: 'Pharmacy Network', icon: Building2, badge: null },
    { id: 'analytics', label: 'Analytics & Baseline', icon: BarChart3, badge: null },
    { id: 'edgecases', label: 'Edge Cases Sandbox', icon: ShieldAlert, badge: '8 Cases' },
    ...(hasRole(['ADMIN', 'MANAGER'])
      ? [{ id: 'audit', label: 'Audit Trail', icon: History, badge: null }]
      : []),
    { id: 'privacy', label: 'Privacy & Consent', icon: Lock, badge: null },
    { id: 'settings', label: 'Settings', icon: Settings, badge: null },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 flex flex-col justify-between shrink-0 select-none">
      <div className="p-4 space-y-6">
        {/* Navigation list */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-glow-emerald'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                      item.highlight
                        ? 'bg-emerald-500 text-slate-950 font-bold'
                        : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* User Scoping Card and Logout at Sidebar Bottom */}
      <div className="p-4 border-t border-slate-900 space-y-2">
        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs">
          <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Current Scope</div>
          <div className="font-semibold text-white mt-0.5 truncate">
            {user?.assigned_pharmacy_id ? `Branch: ${user.assigned_pharmacy_id}` : 'Network-Wide Access'}
          </div>
          <div className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
            <CheckCircle className="w-3 h-3" />
            <span>Role: {user?.role}</span>
          </div>
        </div>

        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-slate-900/50 hover:bg-rose-500/10 border border-slate-800 hover:border-rose-500/30 text-xs text-slate-400 hover:text-rose-300 transition-all font-medium"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
