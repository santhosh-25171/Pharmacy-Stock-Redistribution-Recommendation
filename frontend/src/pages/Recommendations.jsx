import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Search,
  Filter,
  RefreshCw,
  Truck,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Sliders,
  IndianRupee,
  MapPin,
  Clock,
  Eye,
  Check,
} from 'lucide-react';
import { recommendationService, pharmacyService } from '../services/api';
import { RiskBadge } from '../components/RiskBadge';
import { EvidenceModal } from '../components/EvidenceModal';
import { ApprovalModal } from '../components/ApprovalModal';
import { RejectModal } from '../components/RejectModal';
import { OverrideModal } from '../components/OverrideModal';

export const Recommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);

  // Filters
  const [statusFilter, setStatusFilter] = useState('PENDING');
  const [riskFilter, setRiskFilter] = useState('');
  const [highImpactOnly, setHighImpactOnly] = useState(false);
  const [search, setSearch] = useState('');
  const [viewMode, setViewMode] = useState('cards'); // 'cards' or 'table'

  // Modals
  const [selectedRec, setSelectedRec] = useState(null);
  const [isEvidenceOpen, setIsEvidenceOpen] = useState(false);
  const [isApprovalOpen, setIsApprovalOpen] = useState(false);
  const [isRejectOpen, setIsRejectOpen] = useState(false);
  const [isOverrideOpen, setIsOverrideOpen] = useState(false);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const params = {
        status: statusFilter || undefined,
        risk_level: riskFilter || undefined,
        is_high_impact: highImpactOnly ? true : undefined,
      };
      const data = await recommendationService.getRecommendations(params);
      setRecommendations(data);
    } catch (err) {
      console.error('Failed to load recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [statusFilter, riskFilter, highImpactOnly]);

  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      await recommendationService.generate(true);
      await fetchRecommendations();
    } finally {
      setRegenerating(false);
    }
  };

  const handleApprove = async (payload) => {
    if (!selectedRec) return;
    await recommendationService.approve(selectedRec.recommendation_id, payload);
    fetchRecommendations();
  };

  const handleReject = async (payload) => {
    if (!selectedRec) return;
    await recommendationService.reject(selectedRec.recommendation_id, payload);
    fetchRecommendations();
  };

  const handleOverride = async (payload) => {
    if (!selectedRec) return;
    await recommendationService.override(selectedRec.recommendation_id, payload);
    fetchRecommendations();
  };

  const filteredRecs = recommendations.filter((r) => {
    if (!search.trim()) return true;
    const term = search.toLowerCase();
    return (
      r.medicine_name.toLowerCase().includes(term) ||
      r.batch_id.toLowerCase().includes(term) ||
      r.source_pharmacy_name.toLowerCase().includes(term) ||
      r.destination_pharmacy_name.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
        <div>
          <div className="flex items-center gap-2.5">
            <Sparkles className="w-6 h-6 text-emerald-400" />
            <h1 className="text-xl font-black text-white tracking-tight">Stock Redistribution Recommendations</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Explainable, capacity-constrained transfer routes optimizing expiry avoidance and network inventory balance.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="px-3.5 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 flex items-center gap-2 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${regenerating ? 'animate-spin text-emerald-400' : ''}`} />
            {regenerating ? 'Evaluating Network...' : 'Regenerate Recommendations'}
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            {/* Status tabs */}
            {['PENDING', 'APPROVED', 'OVERRIDDEN', 'REJECTED', ''].map((st) => (
              <button
                key={st || 'ALL'}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  statusFilter === st
                    ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                    : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                {st || 'ALL STATUS'}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 text-xs text-slate-300 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl cursor-pointer">
              <input
                type="checkbox"
                checked={highImpactOnly}
                onChange={(e) => setHighImpactOnly(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-emerald-500 w-3.5 h-3.5"
              />
              <span className="font-semibold text-amber-400">High-Impact Only</span>
            </label>

            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-emerald-500"
            >
              <option value="">All Risk Levels</option>
              <option value="CRITICAL">Critical Risk</option>
              <option value="HIGH">High Risk</option>
              <option value="MEDIUM">Medium Risk</option>
            </select>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search recommendation by medicine name, batch code or branch..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      {/* Recommendations Display */}
      {loading ? (
        <div className="py-16 flex flex-col items-center justify-center gap-3">
          <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin" />
          <p className="text-xs text-slate-400">Optimizing transfer routes...</p>
        </div>
      ) : filteredRecs.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filteredRecs.map((rec) => (
            <div
              key={rec.recommendation_id}
              className="p-5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 shadow-lg space-y-4 transition-all"
            >
              {/* Header */}
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-base text-white">{rec.medicine_name}</h3>
                    <RiskBadge risk={rec.risk_level} size="sm" />
                  </div>
                  <div className="flex items-center gap-2 text-xs text-slate-400 mt-1 font-mono">
                    <span>{rec.recommendation_id}</span>
                    <span>&bull;</span>
                    <span>Batch: {rec.batch_id}</span>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-xs text-emerald-400 font-medium">Value Protected</div>
                  <div className="text-lg font-black text-emerald-300">
                    ₹{rec.potential_value_saved.toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Transfer Route Box */}
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 text-xs">
                <div className="grid grid-cols-7 items-center gap-2">
                  <div className="col-span-3 text-left">
                    <div className="text-[11px] text-slate-500 font-semibold uppercase">Source (Excess)</div>
                    <div className="font-bold text-slate-200 truncate">{rec.source_pharmacy_name}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{rec.source_pharmacy_id}</div>
                  </div>

                  <div className="col-span-1 flex flex-col items-center justify-center">
                    <Truck className="w-4 h-4 text-emerald-400" />
                    <ArrowRight className="w-3 h-3 text-slate-500" />
                    <span className="text-[9px] text-slate-400 font-mono">{rec.distance_km}km</span>
                  </div>

                  <div className="col-span-3 text-right">
                    <div className="text-[11px] text-slate-500 font-semibold uppercase">Destination (Demand)</div>
                    <div className="font-bold text-slate-200 truncate">{rec.destination_pharmacy_name}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{rec.destination_pharmacy_id}</div>
                  </div>
                </div>
              </div>

              {/* Metrics Pills */}
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="p-2 rounded-lg bg-slate-950 border border-slate-850">
                  <div className="text-[10px] text-slate-500">Transfer Qty</div>
                  <div className="font-bold text-white font-mono">{rec.recommended_quantity} units</div>
                </div>
                <div className="p-2 rounded-lg bg-slate-950 border border-slate-850">
                  <div className="text-[10px] text-slate-500">Transit Days</div>
                  <div className="font-bold text-blue-400 font-mono">{rec.estimated_transit_days} day(s)</div>
                </div>
                <div className="p-2 rounded-lg bg-slate-950 border border-slate-850">
                  <div className="text-[10px] text-slate-500">Days to Expiry</div>
                  <div className="font-bold text-amber-400 font-mono">{rec.days_to_expiry} days</div>
                </div>
              </div>

              {/* High impact tag if applicable */}
              {rec.is_high_impact && (
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300 font-medium">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                  <span>High-Impact Action: Requires explicit human review before dispatch.</span>
                </div>
              )}

              {/* Override Note display if overridden */}
              {rec.status === 'OVERRIDDEN' && rec.override && (
                <div className="p-2.5 rounded-lg bg-slate-950 border border-amber-500/30 text-xs">
                  <div className="text-amber-400 font-bold text-[11px]">Override Applied: {rec.override.reason_category}</div>
                  {rec.override.custom_reason && (
                    <div className="text-slate-400 text-[11px] mt-0.5">{rec.override.custom_reason}</div>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                <button
                  onClick={() => { setSelectedRec(rec); setIsEvidenceOpen(true); }}
                  className="px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-750 border border-slate-700 rounded-lg flex items-center gap-1.5 transition-colors"
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  Why Recommended?
                </button>

                {rec.status === 'PENDING' ? (
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => { setSelectedRec(rec); setIsRejectOpen(true); }}
                      className="px-3 py-1.5 text-xs font-semibold text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 rounded-lg transition-colors"
                    >
                      Reject
                    </button>
                    <button
                      onClick={() => { setSelectedRec(rec); setIsOverrideOpen(true); }}
                      className="px-3 py-1.5 text-xs font-semibold text-amber-400 hover:text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 rounded-lg transition-colors"
                    >
                      Override
                    </button>
                    <button
                      onClick={() => { setSelectedRec(rec); setIsApprovalOpen(true); }}
                      className="px-3.5 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 shadow-md shadow-emerald-600/20 rounded-lg transition-all"
                    >
                      Approve
                    </button>
                  </div>
                ) : (
                  <div className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    Status: <span className="text-white uppercase">{rec.status}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-12 text-center rounded-2xl bg-slate-900 border border-slate-800">
          <Sparkles className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <h3 className="font-bold text-white text-sm">No Recommendations Found</h3>
          <p className="text-xs text-slate-400 mt-1">Try adjusting the filter criteria or click Regenerate Recommendations.</p>
        </div>
      )}

      {/* Modals */}
      <EvidenceModal
        recommendation={selectedRec}
        isOpen={isEvidenceOpen}
        onClose={() => setIsEvidenceOpen(false)}
        onApprove={(r) => { setSelectedRec(r); setIsApprovalOpen(true); }}
        onReject={(r) => { setSelectedRec(r); setIsRejectOpen(true); }}
        onOverride={(r) => { setSelectedRec(r); setIsOverrideOpen(true); }}
      />

      <ApprovalModal
        recommendation={selectedRec}
        isOpen={isApprovalOpen}
        onClose={() => setIsApprovalOpen(false)}
        onConfirm={handleApprove}
      />

      <RejectModal
        recommendation={selectedRec}
        isOpen={isRejectOpen}
        onClose={() => setIsRejectOpen(false)}
        onConfirm={handleReject}
      />

      <OverrideModal
        recommendation={selectedRec}
        isOpen={isOverrideOpen}
        onClose={() => setIsOverrideOpen(false)}
        onConfirm={handleOverride}
      />
    </div>
  );
};
