import React, { useState, useEffect } from 'react';
import {
  IndianRupee,
  AlertTriangle,
  Sparkles,
  TrendingUp,
  Boxes,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Clock,
  ArrowRight,
  RefreshCw,
  Building2
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
  AreaChart,
  Area,
} from 'recharts';
import { analyticsService, recommendationService } from '../services/api';
import { RiskBadge } from '../components/RiskBadge';
import { EvidenceModal } from '../components/EvidenceModal';
import { ApprovalModal } from '../components/ApprovalModal';
import { RejectModal } from '../components/RejectModal';
import { OverrideModal } from '../components/OverrideModal';

const RISK_COLORS = {
  CRITICAL: '#f43f5e',
  HIGH: '#f59e0b',
  MEDIUM: '#3b82f6',
  LOW: '#10b981',
  EXPIRED: '#a855f7',
};

export const Dashboard = ({ onNavigate }) => {
  const [metrics, setMetrics] = useState(null);
  const [urgentRecs, setUrgentRecs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modal states
  const [selectedRec, setSelectedRec] = useState(null);
  const [isEvidenceOpen, setIsEvidenceOpen] = useState(false);
  const [isApprovalOpen, setIsApprovalOpen] = useState(false);
  const [isRejectOpen, setIsRejectOpen] = useState(false);
  const [isOverrideOpen, setIsOverrideOpen] = useState(false);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [data, recs] = await Promise.all([
        analyticsService.getDashboardMetrics(),
        recommendationService.getRecommendations({ status: 'PENDING' }),
      ]);
      setMetrics(data);
      setUrgentRecs(recs.slice(0, 5));
    } catch (err) {
      console.error('Failed to load dashboard metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleApprove = async (payload) => {
    if (!selectedRec) return;
    await recommendationService.approve(selectedRec.recommendation_id, payload);
    fetchDashboardData();
  };

  const handleReject = async (payload) => {
    if (!selectedRec) return;
    await recommendationService.reject(selectedRec.recommendation_id, payload);
    fetchDashboardData();
  };

  const handleOverride = async (payload) => {
    if (!selectedRec) return;
    await recommendationService.override(selectedRec.recommendation_id, payload);
    fetchDashboardData();
  };

  if (loading || !metrics) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-8rem)]">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin" />
          <p className="text-sm text-slate-400">Loading redistribution intelligence...</p>
        </div>
      </div>
    );
  }

  const riskPieData = Object.entries(metrics.risk_distribution || {}).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="space-y-6">
      {/* Top Banner & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-800 shadow-xl">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-black tracking-tight text-white">Supply Chain Intelligence Dashboard</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-semibold">
              Live Optimization
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time expiry risk detection, localized demand matching, and explainable stock routing across 18 branches.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchDashboardData}
            className="px-3 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 flex items-center gap-2 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Refresh Data
          </button>
          <button
            onClick={() => onNavigate('recommendations')}
            className="px-4 py-2 text-xs font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 flex items-center gap-2 transition-all"
          >
            <Sparkles className="w-3.5 h-3.5" /> View {metrics.pending_recommendations} Recommendations
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Total Inventory Value */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Network Inventory</span>
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Boxes className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-white mt-2">
            ₹{metrics.total_inventory_value.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
            <Building2 className="w-3 h-3 text-slate-500" />
            <span>Across 18 pharmacies & 5,000+ batches</span>
          </div>
        </div>

        {/* Card 2: Near-Expiry At Risk Value */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Stock Value At Expiry Risk</span>
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-amber-400 mt-2">
            ₹{metrics.near_expiry_stock_value.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            <span className="font-bold text-rose-400">{metrics.high_risk_batches_count}</span> batches within critical/high window
          </div>
        </div>

        {/* Card 3: Potential Value Protected */}
        <div className="p-5 rounded-2xl bg-emerald-950/40 border border-emerald-500/30 shadow-glow-emerald">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-emerald-400">Potential Value Protected</span>
            <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-emerald-300 mt-2">
            ₹{metrics.potential_value_saved.toLocaleString()}
          </div>
          <div className="text-[11px] text-emerald-400/80 mt-1 flex items-center gap-1">
            <TrendingUp className="w-3 h-3 text-emerald-400" />
            <span>Identified by Redistribution Recommender</span>
          </div>
        </div>

        {/* Card 4: Value Transferred & Decision Rates */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Transferred / Value Used</span>
            <div className="p-2 rounded-xl bg-teal-500/10 text-teal-400 border border-teal-500/20">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-white mt-2">
            ₹{metrics.value_successfully_transferred.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-2">
            <span className="text-emerald-400 font-semibold">{metrics.approval_rate_pct}% Appr</span>
            <span>&bull;</span>
            <span className="text-rose-400 font-semibold">{metrics.rejection_rate_pct}% Rej</span>
            <span>&bull;</span>
            <span className="text-amber-400 font-semibold">{metrics.override_rate_pct}% Ovr</span>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart 1: Near-Expiry Stock by Pharmacy (2 cols) */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white">Near-Expiry Stock Value by Pharmacy</h3>
              <p className="text-xs text-slate-400">Branches with highest capital exposure in the next 30 days</p>
            </div>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
              Top 8 Branches
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metrics.near_expiry_by_pharmacy.slice(0, 8)} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                <XAxis
                  dataKey="pharmacy_id"
                  stroke="#64748b"
                  fontSize={11}
                  tickLine={false}
                />
                <YAxis
                  stroke="#64748b"
                  fontSize={11}
                  tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
                  tickLine={false}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="p-3 rounded-xl bg-slate-950 border border-slate-700 text-xs shadow-xl space-y-1">
                          <div className="font-bold text-white">{d.pharmacy_name}</div>
                          <div className="text-slate-400 font-mono text-[10px]">{d.pharmacy_id}</div>
                          <div className="text-amber-400 font-semibold">₹{d.near_expiry_value.toLocaleString()}</div>
                          <div className="text-[11px] text-slate-400">{d.near_expiry_batches} risky batches</div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="near_expiry_value" fill="#f59e0b" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Expiry Risk Distribution (1 col) */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white">Batch Risk Distribution</h3>
            <p className="text-xs text-slate-400">Segmentation across 5,000+ active batches</p>
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {riskPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={RISK_COLORS[entry.name] || '#64748b'} />
                  ))}
                </Pie>
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0];
                      return (
                        <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs shadow-lg">
                          <span className="font-bold text-white">{d.name}: </span>
                          <span className="text-slate-300 font-mono">{d.value} batches</span>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  formatter={(val) => <span className="text-[11px] text-slate-300">{val}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Urgent Recommendations Queue */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-white">Urgent Redistribution Recommendations</h3>
          </div>
          <button
            onClick={() => onNavigate('recommendations')}
            className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1"
          >
            View All ({metrics.total_recommendations}) <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="divide-y divide-slate-800">
          {urgentRecs.length > 0 ? (
            urgentRecs.map((rec) => (
              <div
                key={rec.recommendation_id}
                className="py-3.5 flex flex-col md:flex-row md:items-center justify-between gap-3 hover:bg-slate-850/50 p-2 rounded-xl transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-white">{rec.medicine_name}</span>
                    <RiskBadge risk={rec.risk_level} size="sm" />
                    {rec.is_high_impact && (
                      <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
                        High Impact
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-400 flex items-center gap-2">
                    <span className="font-mono">{rec.batch_id}</span>
                    <span>&bull;</span>
                    <span>{rec.source_pharmacy_name} → {rec.destination_pharmacy_name}</span>
                    <span>&bull;</span>
                    <span className="text-slate-300">{rec.days_to_expiry}d to expiry</span>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-xs font-bold text-emerald-400">
                      ₹{rec.potential_value_saved.toLocaleString()}
                    </div>
                    <div className="text-[11px] text-slate-400">{rec.recommended_quantity} units</div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => { setSelectedRec(rec); setIsEvidenceOpen(true); }}
                      className="px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-750 border border-slate-700 rounded-lg transition-colors"
                    >
                      Why?
                    </button>
                    <button
                      onClick={() => { setSelectedRec(rec); setIsApprovalOpen(true); }}
                      className="px-3 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 rounded-lg shadow-md shadow-emerald-600/20 transition-all"
                    >
                      Approve
                    </button>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-xs text-slate-400">
              No pending recommendations requiring immediate review.
            </div>
          )}
        </div>
      </div>

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
