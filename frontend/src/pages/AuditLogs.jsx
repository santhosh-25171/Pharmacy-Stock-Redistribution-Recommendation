import React, { useState, useEffect } from 'react';
import { History, Search, Filter, RefreshCw, ShieldCheck, UserCheck, Clock, FileText } from 'lucide-react';
import { auditService } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const AuditLogs = () => {
  const { hasRole } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('');
  const [search, setSearch] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await auditService.getLogs({ action: actionFilter || undefined });
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [actionFilter]);

  if (!hasRole(['ADMIN', 'MANAGER'])) {
    return (
      <div className="p-12 text-center rounded-2xl bg-slate-900 border border-slate-800">
        <ShieldCheck className="w-8 h-8 text-rose-500 mx-auto mb-2" />
        <h3 className="text-sm font-bold text-white">Access Restricted</h3>
        <p className="text-xs text-slate-400 mt-1">Audit log inspection requires Administrator or Manager role privileges.</p>
      </div>
    );
  }

  const filteredLogs = logs.filter((l) => {
    if (!search.trim()) return true;
    const term = search.toLowerCase();
    return (
      l.user_email.toLowerCase().includes(term) ||
      (l.recommendation_id && l.recommendation_id.toLowerCase().includes(term)) ||
      (l.reason && l.reason.toLowerCase().includes(term)) ||
      l.action.toLowerCase().includes(term)
    );
  });

  const getActionBadge = (action) => {
    switch (action) {
      case 'APPROVED':
        return <span className="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-bold text-[10px] border border-emerald-500/30">APPROVED</span>;
      case 'REJECTED':
        return <span className="px-2 py-0.5 rounded bg-rose-500/15 text-rose-400 font-bold text-[10px] border border-rose-500/30">REJECTED</span>;
      case 'OVERRIDDEN':
        return <span className="px-2 py-0.5 rounded bg-amber-500/15 text-amber-400 font-bold text-[10px] border border-amber-500/30">OVERRIDDEN</span>;
      case 'GENERATED':
        return <span className="px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 font-bold text-[10px] border border-blue-500/30">GENERATED</span>;
      case 'SEEDED':
        return <span className="px-2 py-0.5 rounded bg-purple-500/15 text-purple-400 font-bold text-[10px] border border-purple-500/30">SEEDED</span>;
      default:
        return <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold text-[10px]">{action}</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
        <div>
          <div className="flex items-center gap-2.5">
            <History className="w-6 h-6 text-emerald-400" />
            <h1 className="text-xl font-black text-white tracking-tight">Compliance & Decision Audit Trail</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Immutable log of all automated recommendations, approvals, rejections, overrides, and user interactions.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="px-3.5 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 flex items-center gap-2 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-emerald-400' : ''}`} /> Refresh Log
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg flex flex-col md:flex-row gap-3">
        <div className="flex-1 relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by user email, recommendation ID or notes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>

        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          className="px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-emerald-500"
        >
          <option value="">All Audit Actions</option>
          <option value="APPROVED">Approved</option>
          <option value="REJECTED">Rejected</option>
          <option value="OVERRIDDEN">Overridden</option>
          <option value="GENERATED">Generated</option>
          <option value="SEEDED">Database Seeded</option>
        </select>
      </div>

      {/* Audit Log Table */}
      <div className="rounded-2xl bg-slate-900 border border-slate-800 shadow-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-850/60 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Actor / Role</th>
                <th className="py-3 px-4">Recommendation ID</th>
                <th className="py-3 px-4">State Transition</th>
                <th className="py-3 px-4 text-right">Quantity</th>
                <th className="py-3 px-4">Reason / Dispatch Note</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-xs">
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 text-emerald-400 animate-spin mx-auto mb-2" />
                    Fetching audit trail...
                  </td>
                </tr>
              ) : filteredLogs.length > 0 ? (
                filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-850/50 transition-colors">
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-400">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3 px-4">{getActionBadge(log.action)}</td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-white">{log.user_email}</div>
                      <span className="text-[10px] font-mono text-emerald-400 uppercase">{log.user_role}</span>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-300">
                      {log.recommendation_id || '-'}
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px]">
                      {log.previous_state ? (
                        <span className="text-slate-400">
                          {log.previous_state} → <strong className="text-white">{log.new_state}</strong>
                        </span>
                      ) : (
                        <span className="text-slate-600">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-slate-200">
                      {log.quantity ? `${log.quantity} units` : '-'}
                    </td>
                    <td className="py-3 px-4 text-slate-300 text-[11px] max-w-xs truncate">
                      {log.reason || '-'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-400">
                    No audit records match the selected filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
