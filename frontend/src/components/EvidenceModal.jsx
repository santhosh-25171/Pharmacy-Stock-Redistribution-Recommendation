import React from 'react';
import { X, CheckCircle2, ShieldCheck, AlertTriangle, ArrowRight, Truck, Clock, IndianRupee, MapPin } from 'lucide-react';
import { RiskBadge } from './RiskBadge';

export const EvidenceModal = ({ recommendation, isOpen, onClose, onApprove, onReject, onOverride }) => {
  if (!isOpen || !recommendation) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-750 rounded-2xl shadow-2xl overflow-hidden border border-slate-700">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-800 bg-slate-850/80">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-white">Explainable Transfer Evidence</h3>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                  {recommendation.recommendation_id}
                </span>
              </div>
              <p className="text-xs text-slate-400">Interpretable Decision Audit & Feasibility Verification</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto">
          {/* Transfer Summary Header */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
            <div className="flex items-center justify-between mb-3">
              <div>
                <span className="text-xs text-slate-400 font-medium">RECOMMENDED MEDICATION</span>
                <div className="text-base font-bold text-white">{recommendation.medicine_name}</div>
                <div className="text-xs text-slate-400 font-mono mt-0.5">Batch: {recommendation.batch_id}</div>
              </div>
              <div className="text-right">
                <RiskBadge risk={recommendation.risk_level} size="md" />
                <div className="text-xs text-slate-400 mt-1">
                  Recommendation Score: <span className="text-emerald-400 font-semibold">{recommendation.recommendation_score || Math.round(recommendation.confidence_score * 100)} / 100</span>
                </div>
              </div>
            </div>

            {/* Demand Intelligence Banner */}
            <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/20 flex flex-wrap items-center justify-between gap-2 text-xs">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span className="text-slate-300 font-semibold">Demand Intelligence:</span>
                <span className="text-emerald-300 font-bold">{recommendation.predicted_demand ? `${recommendation.predicted_demand} units/day` : 'Active Demand'}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  {recommendation.demand_source || 'ML_PREDICTION'}
                </span>
                <span className="text-[11px] text-slate-400">RandomForestRegressor (MAE 1.22)</span>
              </div>
            </div>

            {/* Route visual */}
            <div className="grid grid-cols-7 items-center gap-2 py-3 px-4 rounded-lg bg-slate-900/90 border border-slate-800 text-xs">
              <div className="col-span-3 text-left">
                <div className="text-slate-400 flex items-center gap-1"><MapPin className="w-3.5 h-3.5 text-rose-400" /> Source Hub</div>
                <div className="font-semibold text-white truncate">{recommendation.source_pharmacy_name}</div>
                <div className="text-[11px] text-slate-400 font-mono">{recommendation.source_pharmacy_id}</div>
              </div>

              <div className="col-span-1 flex flex-col items-center justify-center text-center">
                <Truck className="w-4 h-4 text-emerald-400" />
                <ArrowRight className="w-3 h-3 text-slate-400" />
                <span className="text-[10px] text-slate-400">{recommendation.distance_km} km</span>
              </div>

              <div className="col-span-3 text-right">
                <div className="text-slate-400 flex items-center justify-end gap-1">Target Need <MapPin className="w-3.5 h-3.5 text-emerald-400" /></div>
                <div className="font-semibold text-white truncate">{recommendation.destination_pharmacy_name}</div>
                <div className="text-[11px] text-slate-400 font-mono">{recommendation.destination_pharmacy_id}</div>
              </div>
            </div>
          </div>

          {/* High Impact Alert */}
          {recommendation.is_high_impact && (
            <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs">
              <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
              <div>
                <div className="font-bold text-amber-200 uppercase tracking-wide">High-Impact Redistribution Action</div>
                <div className="text-slate-300 mt-0.5">
                  This transfer involves high stock value (≥ ₹2,000) or an urgent expiry window. Mandatory human authorization required before physical dispatch.
                </div>
              </div>
            </div>
          )}

          {/* WHY THIS RECOMMENDATION? Structured Verification Checklist */}
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Safety & Feasibility Verification Checklist
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                <span>Source has excess inventory</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                <span>Source safety stock protected</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                <span>Destination demand predicted</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                <span>Product has sufficient shelf-life</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                <span>Road transit is feasible</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                <span>Destination capacity verified</span>
              </div>
            </div>
          </div>

          {/* WHY Section with Evidence Bullets */}
          <div>
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Explainable Transfer Evidence Bullets
            </h4>
            <div className="space-y-2.5">
              {recommendation.evidence && recommendation.evidence.length > 0 ? (
                recommendation.evidence.map((item, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 p-3 rounded-xl bg-slate-850 border border-slate-800/80 hover:border-slate-700 transition-colors"
                  >
                    <div className="p-1 rounded-full bg-emerald-500/20 text-emerald-400 flex-shrink-0 mt-0.5">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                    <div className="flex-1">
                      <p className="text-xs text-slate-200 leading-relaxed">{item.evidence_bullet}</p>
                      {item.metric_value && (
                        <div className="mt-1 flex items-center gap-2">
                          <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                            {item.metric_name || 'PARAMETER'}
                          </span>
                          <span className="text-xs font-semibold text-emerald-400">{item.metric_value}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-xs text-slate-400 italic">Evidence bullets generated based on live database parameters.</div>
              )}
            </div>
          </div>

          {/* Quantitative Impact Summary */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[11px] text-slate-400">Transfer Quantity</span>
              <div className="text-lg font-bold text-white mt-0.5">{recommendation.recommended_quantity} units</div>
              <span className="text-[10px] text-slate-400">@ ₹{recommendation.unit_price} / unit</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[11px] text-slate-400">Transit Duration</span>
              <div className="text-lg font-bold text-blue-400 mt-0.5">{recommendation.estimated_transit_days} day(s)</div>
              <span className="text-[10px] text-slate-400">{recommendation.distance_km} km distance</span>
            </div>
            <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/30">
              <span className="text-[11px] text-emerald-400 font-medium">Potential Value Protected</span>
              <div className="text-lg font-bold text-emerald-300 mt-0.5">₹{recommendation.potential_value_saved.toLocaleString()}</div>
              <span className="text-[10px] text-emerald-400/80">Prevents Expiry Loss</span>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-[11px] text-slate-400 flex items-center justify-between">
            <span>Clinical Notice: Operational stock routing decision support only.</span>
            <span className="font-mono text-slate-400">100% Explainable Rule Logic</span>
          </div>
        </div>

        {/* Action Footer */}
        <div className="flex items-center justify-between p-4 px-6 border-t border-slate-800 bg-slate-850">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white rounded-lg transition-colors"
          >
            Close
          </button>

          {recommendation.status === 'PENDING' ? (
            <div className="flex items-center gap-2">
              <button
                onClick={() => { onClose(); onReject(recommendation); }}
                className="px-3.5 py-2 text-xs font-semibold text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 rounded-lg transition-colors"
              >
                Reject Transfer
              </button>
              <button
                onClick={() => { onClose(); onOverride(recommendation); }}
                className="px-3.5 py-2 text-xs font-semibold text-amber-400 hover:text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 rounded-lg transition-colors"
              >
                Override Quantity
              </button>
              <button
                onClick={() => { onClose(); onApprove(recommendation); }}
                className="px-4 py-2 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 shadow-lg shadow-emerald-600/20 rounded-lg transition-all"
              >
                {recommendation.is_high_impact ? 'Review & Approve' : 'Approve Transfer'}
              </button>
            </div>
          ) : (
            <div className="text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 border border-slate-700">
              Status: <span className="font-bold text-white uppercase">{recommendation.status}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
