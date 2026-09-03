import React, { useState, useEffect } from 'react';
import { ShieldAlert, ShieldCheck, CheckCircle2, XCircle, AlertTriangle, RefreshCw } from 'lucide-react';
import { edgeCaseService } from '../services/api';

export const EdgeCases = () => {
  const [edgeCases, setEdgeCases] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchEdgeCases = async () => {
    setLoading(true);
    try {
      const data = await edgeCaseService.getEdgeCases();
      setEdgeCases(data);
    } catch (err) {
      console.error('Failed to load edge cases:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEdgeCases();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
        <div>
          <div className="flex items-center gap-2.5">
            <ShieldAlert className="w-6 h-6 text-amber-400" />
            <h1 className="text-xl font-black text-white tracking-tight">Operational Safety & Edge Case Sandbox</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Systematic stress-testing and clinical safety constraints verifying that hazardous or infeasible transfers are strictly blocked.
          </p>
        </div>

        <button
          onClick={fetchEdgeCases}
          className="px-3.5 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 flex items-center gap-2 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-emerald-400' : ''}`} /> Re-verify Safety Engine
        </button>
      </div>

      {/* Grid of 8 Edge Cases */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3">
          <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin" />
          <p className="text-xs text-slate-400">Verifying edge case safety rules...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {edgeCases.map((ec) => (
            <div
              key={ec.case_number}
              className="p-5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 shadow-lg space-y-3 transition-all"
            >
              {/* Header */}
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="text-[10px] font-mono font-bold uppercase text-emerald-400">
                    CASE 0{ec.case_number} &bull; TAG: {ec.batch_tag}
                  </div>
                  <h3 className="font-bold text-sm text-white mt-0.5">{ec.title}</h3>
                </div>

                {ec.is_blocked ? (
                  <span className="px-2.5 py-1 rounded-full bg-rose-500/15 text-rose-400 border border-rose-500/30 text-xs font-bold flex items-center gap-1">
                    <XCircle className="w-3.5 h-3.5" /> BLOCKED
                  </span>
                ) : (
                  <span className="px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 text-xs font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> RE-ROUTED
                  </span>
                )}
              </div>

              {/* Description */}
              <p className="text-xs text-slate-300 leading-relaxed bg-slate-950 p-3 rounded-xl border border-slate-850">
                {ec.description}
              </p>

              {/* Behavior Comparison */}
              <div className="space-y-1.5 text-xs">
                <div className="flex items-start gap-2">
                  <span className="text-slate-500 font-semibold min-w-[90px]">Expected:</span>
                  <span className="text-slate-300">{ec.expected_result}</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-slate-500 font-semibold min-w-[90px]">Actual System:</span>
                  <span className="font-bold text-emerald-400">{ec.actual_system_behavior}</span>
                </div>
              </div>

              {/* Safety Rule Applied Footer */}
              <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-400 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span className="font-mono text-slate-400">{ec.safety_rule_applied}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
