import React, { useState, useEffect } from 'react';
import { Shield, Activity, User, ChevronDown, Check, Building2, Lock, HelpCircle, LogOut } from 'lucide-react';
import { useAuth, DEMO_ACCOUNTS } from '../context/AuthContext';
import { systemService } from '../services/api';

export const Navbar = ({ onOpenPrivacy }) => {
  const { user, loginAsDemo, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [systemHealth, setSystemHealth] = useState('checking');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await systemService.getHealth();
        setSystemHealth('healthy');
      } catch (err) {
        setSystemHealth('degraded');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSwitchAccount = async (email) => {
    setDropdownOpen(false);
    await loginAsDemo(email);
  };

  const handleLogout = () => {
    setDropdownOpen(false);
    logout();
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand & Prototype Label */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-extrabold text-base tracking-tight text-white">PharmaShift</span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              Redistribution AI
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium">Expiry-Aware Pharmacy Network Optimizer</p>
        </div>
      </div>

      {/* Center Notice: Synthetic Data Guarantee */}
      <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-950/80 border border-slate-800 text-[11px] text-slate-400">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>100% Synthetic Operational Data &bull; Zero Real Patient PII</span>
      </div>

      {/* Right Controls: Health & Demo Role Switcher & Logout */}
      <div className="flex items-center gap-3">
        {/* System Health Badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-xs">
          <Activity className={`w-3.5 h-3.5 ${systemHealth === 'healthy' ? 'text-emerald-400' : 'text-amber-400'}`} />
          <span className="text-[11px] text-slate-400 capitalize">{systemHealth} API</span>
        </div>

        {/* Demo Account Switcher Dropdown */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-850 hover:bg-slate-800 border border-slate-700/80 text-xs text-slate-200 transition-all"
          >
            <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-[10px]">
              {user?.role ? user.role[0] : 'U'}
            </div>
            <div className="text-left hidden md:block">
              <div className="font-semibold text-white leading-tight">{user?.full_name || 'User'}</div>
              <div className="text-[10px] text-emerald-400 font-mono">
                {user?.role} {user?.assigned_pharmacy_id ? `(${user.assigned_pharmacy_id})` : '(Network)'}
              </div>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-72 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl py-2 z-50 animate-in fade-in zoom-in-95 duration-150">
              <div className="px-3 py-2 border-b border-slate-800 text-[11px] text-slate-400 font-semibold uppercase tracking-wider">
                Switch Demo Persona / Role
              </div>
              <div className="py-1">
                {DEMO_ACCOUNTS.map((acc) => {
                  const isCurrent = user?.email === acc.email;
                  return (
                    <button
                      key={acc.email}
                      onClick={() => handleSwitchAccount(acc.email)}
                      className={`w-full px-3 py-2 text-left text-xs flex items-center justify-between hover:bg-slate-800 transition-colors ${
                        isCurrent ? 'bg-emerald-500/10 text-emerald-300 font-semibold' : 'text-slate-300'
                      }`}
                    >
                      <div>
                        <div className="font-medium text-white">{acc.label}</div>
                        <div className="text-[10px] text-slate-400 font-mono">{acc.email}</div>
                      </div>
                      {isCurrent && <Check className="w-4 h-4 text-emerald-400" />}
                    </button>
                  );
                })}
              </div>
              <div className="border-t border-slate-800 pt-1 px-2 space-y-1">
                <button
                  onClick={() => { setDropdownOpen(false); if (onOpenPrivacy) onOpenPrivacy(); }}
                  className="w-full px-2 py-1.5 text-left text-xs text-slate-400 hover:text-slate-200 rounded flex items-center gap-2"
                >
                  <Lock className="w-3.5 h-3.5" /> Privacy & Consent Policy
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full px-2 py-1.5 text-left text-xs text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 rounded flex items-center gap-2 transition-colors font-medium"
                >
                  <LogOut className="w-3.5 h-3.5" /> Sign Out
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Visible Direct Logout Button */}
        <button
          onClick={handleLogout}
          title="Sign out of PharmaShift"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-rose-500/15 border border-slate-800 hover:border-rose-500/30 text-xs text-slate-400 hover:text-rose-300 transition-all font-medium"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Sign Out</span>
        </button>
      </div>
    </header>
  );
};

export default Navbar;
