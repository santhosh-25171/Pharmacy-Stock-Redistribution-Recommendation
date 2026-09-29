import React, { useState } from 'react';
import { Sliders, RefreshCw, Shield, Database, CheckCircle2, AlertTriangle, Key, ShieldAlert } from 'lucide-react';
import { systemService } from '../services/api';
import { DEMO_ACCOUNTS, useAuth } from '../context/AuthContext';

export const Settings = () => {
  const { user, hasRole } = useAuth();
  const [valThreshold, setValThreshold] = useState(2000);
  const [qtyThreshold, setQtyThreshold] = useState(50);
  const [dteThreshold, setDteThreshold] = useState(14);
  const [isReseeding, setIsReseeding] = useState(false);
  const [reseedSuccess, setReseedSuccess] = useState(false);
  const [reseedError, setReseedError] = useState(null);

  const handleReseed = async () => {
    if (!hasRole(['ADMIN'])) {
      alert('Access Denied: Database re-seeding requires the ADMIN role. Current account lacks permission.');
      return;
    }
    if (!window.confirm('Are you sure you want to reset the database and re-seed 5,000+ synthetic records?')) {
      return;
    }
    setIsReseeding(true);
    setReseedSuccess(false);
    setReseedError(null);
    try {
      await systemService.reseed();
      setReseedSuccess(true);
      setTimeout(() => setReseedSuccess(false), 4000);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to reseed database.';
      setReseedError(msg);
      alert(`Re-seeding failed: ${msg}`);
    } finally {
      setIsReseeding(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
        <div className="flex items-center gap-2.5">
          <Sliders className="w-6 h-6 text-emerald-400" />
          <h1 className="text-xl font-black text-white tracking-tight">System & Policy Settings</h1>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Configure human-in-the-loop escalation thresholds, evaluate safety policies, and manage database lifecycle.
        </p>
      </div>

      {/* High Impact Threshold Configuration */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-4">
        <div>
          <h3 className="font-bold text-sm text-white flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            Human-in-the-Loop Escalation Rules
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Recommendations exceeding these thresholds trigger mandatory human confirmation dialogs.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <label className="block text-xs font-semibold text-slate-300">
              High-Value Cutoff (₹ INR)
            </label>
            <input
              type="number"
              value={valThreshold}
              onChange={(e) => setValThreshold(parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 text-sm font-bold bg-slate-900 border border-slate-750 rounded-lg text-emerald-400 focus:outline-none focus:border-emerald-500"
            />
            <span className="text-[10px] text-slate-500">Transfers ≥ this value flagged as High-Impact</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <label className="block text-xs font-semibold text-slate-300">
              Large Volume Cutoff (Units)
            </label>
            <input
              type="number"
              value={qtyThreshold}
              onChange={(e) => setQtyThreshold(parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 text-sm font-bold bg-slate-900 border border-slate-750 rounded-lg text-blue-400 focus:outline-none focus:border-emerald-500"
            />
            <span className="text-[10px] text-slate-500">Batch transfers ≥ this size require review</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <label className="block text-xs font-semibold text-slate-300">
              Urgent Expiry Window (Days)
            </label>
            <input
              type="number"
              value={dteThreshold}
              onChange={(e) => setDteThreshold(parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 text-sm font-bold bg-slate-900 border border-slate-750 rounded-lg text-amber-400 focus:outline-none focus:border-emerald-500"
            />
            <span className="text-[10px] text-slate-500">Batches with ≤ this remaining life flagged</span>
          </div>
        </div>
      </div>

      {/* Demo Credentials Table */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-3">
        <h3 className="font-bold text-sm text-white flex items-center gap-2">
          <Key className="w-4 h-4 text-emerald-400" />
          Pre-Configured Demo Personas
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] font-bold">
                <th className="py-2.5 px-3">Role</th>
                <th className="py-2.5 px-3">Email Account</th>
                <th className="py-2.5 px-3">Password</th>
                <th className="py-2.5 px-3">Permission Scope</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {DEMO_ACCOUNTS.map((acc) => (
                <tr key={acc.email} className="hover:bg-slate-850/50">
                  <td className="py-2.5 px-3 font-bold text-emerald-400">{acc.role}</td>
                  <td className="py-2.5 px-3 font-mono text-white">{acc.email}</td>
                  <td className="py-2.5 px-3 font-mono text-slate-400">
                    {acc.email.startsWith('admin') ? 'Admin@123' : (acc.email.startsWith('manager') ? 'Manager@123' : 'Pharmacist@123')}
                  </td>
                  <td className="py-2.5 px-3 text-slate-300">{acc.label}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Database Management Card */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h3 className="font-bold text-sm text-white flex items-center gap-2">
            <Database className="w-4 h-4 text-purple-400" />
            Synthetic Database Re-Seeding
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Reset database tables, repopulate 5,000+ inventory batches, and regenerate initial recommendation records.
          </p>
        </div>

        <button
          onClick={handleReseed}
          disabled={isReseeding}
          className="px-4 py-2 text-xs font-semibold rounded-xl bg-purple-600 hover:bg-purple-500 text-white shadow-md shadow-purple-600/20 flex items-center gap-2 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isReseeding ? 'animate-spin' : ''}`} />
          {isReseeding ? 'Resetting DB...' : 'Re-Seed 5,000+ Records'}
        </button>
      </div>

      {reseedSuccess && (
        <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          <span>Database successfully reset and re-populated with 5,000+ batches and fresh recommendations!</span>
        </div>
      )}
    </div>
  );
};
