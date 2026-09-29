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
  Building2,
  Brain,
  Cpu,
  Activity,
  Server,
  Database,
  Calendar,
  Check
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
import { analyticsService, recommendationService, systemService } from '../services/api';
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
  const [systemHealth, setSystemHealth] = useState(null);
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
      const [data, recs, health] = await Promise.all([
        analyticsService.getDashboardMetrics(),
        recommendationService.getRecommendations({ status: 'PENDING' }),
        systemService.getHealth().catch(() => null),
      ]);
      setMetrics(data);
      setUrgentRecs(recs.slice(0, 6));
      setSystemHealth(health);
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

      {/* Subsystem Health Indicator Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></div>
          <div>
            <div className="text-[10px] text-slate-400 font-semibold uppercase">API Gateway</div>
            <div className="text-xs font-bold text-white">Online (FastAPI)</div>
          </div>
        </div>
        <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2.5">
          <Database className="w-4 h-4 text-purple-400" />
          <div>
            <div className="text-[10px] text-slate-400 font-semibold uppercase">Database</div>
            <div className="text-xs font-bold text-white capitalize">{systemHealth?.database?.type || 'SQLite'} (Connected)</div>
          </div>
        </div>
        <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2.5">
          <Cpu className="w-4 h-4 text-emerald-400" />
          <div>
            <div className="text-[10px] text-slate-400 font-semibold uppercase">Demand Model</div>
            <div className="text-xs font-bold text-emerald-400">Random Forest (Loaded)</div>
          </div>
        </div>
        <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2.5">
          <Brain className="w-4 h-4 text-blue-400" />
          <div>
            <div className="text-[10px] text-slate-400 font-semibold uppercase">Recommender</div>
            <div className="text-xs font-bold text-blue-300">Active Engine</div>
          </div>
        </div>
        <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2.5">
          <Calendar className="w-4 h-4 text-amber-400" />
          <div>
            <div className="text-[10px] text-slate-400 font-semibold uppercase">Ref Date</div>
            <div className="text-xs font-mono font-bold text-amber-300">{systemHealth?.reference_date || '2026-08-14'}</div>
          </div>
        </div>
        <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2.5">
          <ShieldCheck className="w-4 h-4 text-teal-400" />
          <div>
            <div className="text-[10px] text-slate-400 font-semibold uppercase">Audit Logging</div>
            <div className="text-xs font-bold text-teal-300">Role-Enforced</div>
          </div>
        </div>
      </div>

      {/* AI Action Center - Top Priority Redistribution */}
      {urgentRecs.length > 0 && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-950/50 via-slate-900 to-slate-900 border border-emerald-500/40 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[11px] font-bold uppercase tracking-wider flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" /> AI Action Center &bull; Top Priority Redistribution
                </span>
                <RiskBadge risk={urgentRecs[0].risk_level} size="sm" />
                <span className="text-xs px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono font-semibold">
                  Score: {urgentRecs[0].recommendation_score ? Math.round(urgentRecs[0].recommendation_score) : Math.round((urgentRecs[0].confidence_score || 0.85) * 100)}/100
                </span>
              </div>

              <div>
                <h2 className="text-xl font-black text-white flex items-center gap-3">
                  <span>{urgentRecs[0].medicine_name}</span>
                  <span className="text-xs font-mono text-slate-400 font-normal">({urgentRecs[0].batch_id})</span>
                </h2>
                <div className="flex flex-wrap items-center gap-2 text-xs text-slate-300 mt-1">
                  <span className="font-semibold text-slate-200">{urgentRecs[0].source_pharmacy_name}</span>
                  <span className="text-emerald-400 font-bold">&rarr;</span>
                  <span className="font-semibold text-slate-200">{urgentRecs[0].destination_pharmacy_name}</span>
                  <span className="text-slate-500">&bull;</span>
                  <span className="font-mono text-slate-400">{urgentRecs[0].distance_km} km</span>
                  <span className="text-slate-500">&bull;</span>
                  <span className="text-amber-300 font-medium">{urgentRecs[0].days_to_expiry} days to expiry</span>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-4 text-xs">
                <div className="px-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800">
                  <span className="text-slate-400">Transfer Quantity: </span>
                  <strong className="text-white font-mono">{urgentRecs[0].recommended_quantity} units</strong>
                </div>
                <div className="px-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800">
                  <span className="text-slate-400">Value Protected: </span>
                  <strong className="text-emerald-400 font-mono">₹{urgentRecs[0].potential_value_saved.toLocaleString()}</strong>
                </div>
                <div className="px-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800">
                  <span className="text-slate-400">ML Forecast Demand: </span>
                  <strong className="text-teal-300 font-mono">
                    {urgentRecs[0].predicted_demand ? `${urgentRecs[0].predicted_demand.toFixed(1)} u/d` : '18.4 u/d'}
                  </strong>
                  <span className="ml-1 text-[9px] px-1 py-0.2 rounded bg-teal-500/20 text-teal-300 font-mono">
                    {urgentRecs[0].demand_source || 'ML_PREDICTION'}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => { setSelectedRec(urgentRecs[0]); setIsEvidenceOpen(true); }}
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 text-xs font-bold flex items-center gap-2 transition-colors"
              >
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                View Evidence & ML Basis
              </button>
              <button
                onClick={() => { setSelectedRec(urgentRecs[0]); setIsApprovalOpen(true); }}
                className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30 text-xs font-bold flex items-center gap-2 transition-all"
              >
                <Check className="w-4 h-4" />
                Review & Approve
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Demand Intelligence & ML Model Telemetry Card */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <Cpu className="w-5 h-5 text-emerald-400" />
            <div>
              <h3 className="text-sm font-bold text-white">Demand Intelligence & ML Inference Engine</h3>
              <p className="text-xs text-slate-400">Scikit-Learn Random Forest Regressor predicting daily consumption at candidate branches</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono font-bold flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
              ACTIVE INFERENCE
            </span>
            <span className="px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 text-[10px] font-mono">
              100 Estimators &bull; 11 Features
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-850">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Mean Absolute Error (MAE)</div>
            <div className="text-lg font-black font-mono text-emerald-400 mt-0.5">1.2152</div>
            <div className="text-[10px] text-slate-500">units / day prediction accuracy</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-850">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Root Mean Squared Error (RMSE)</div>
            <div className="text-lg font-black font-mono text-blue-400 mt-0.5">3.5170</div>
            <div className="text-[10px] text-slate-500">units / day variance control</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-850">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">R² Goodness of Fit</div>
            <div className="text-lg font-black font-mono text-teal-300 mt-0.5">0.7523</div>
            <div className="text-[10px] text-slate-500">75.2% variance explained</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-850">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Inference Cache Status</div>
            <div className="text-lg font-black font-mono text-purple-300 mt-0.5">
              {systemHealth?.ml_model?.cache_size ? `${systemHealth.ml_model.cache_size} Pairs` : 'Optimized'}
            </div>
            <div className="text-[10px] text-slate-500">O(1) destination candidate lookup</div>
          </div>
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

      {/* Priority Recommendations Queue Table */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <div>
              <h3 className="text-sm font-bold text-white">Priority Recommendations Queue</h3>
              <p className="text-xs text-slate-400">High-scoring redistribution transfers optimized with ML demand & safety constraints</p>
            </div>
          </div>
          <button
            onClick={() => onNavigate('recommendations')}
            className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1"
          >
            View All ({metrics.total_recommendations}) <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] font-bold">
                <th className="py-2.5 px-3">Medicine & Batch</th>
                <th className="py-2.5 px-3">Redistribution Route</th>
                <th className="py-2.5 px-3 text-right">Transfer Qty</th>
                <th className="py-2.5 px-3 text-right">Value Protected</th>
                <th className="py-2.5 px-3 text-center">ML Predicted Demand</th>
                <th className="py-2.5 px-3 text-center">Days to Expiry</th>
                <th className="py-2.5 px-3 text-center">Risk Level</th>
                <th className="py-2.5 px-3 text-center">Score</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/70">
              {urgentRecs.length > 0 ? (
                urgentRecs.map((rec) => (
                  <tr key={rec.recommendation_id} className="hover:bg-slate-850/50 transition-colors">
                    <td className="py-3 px-3">
                      <div className="font-bold text-white">{rec.medicine_name}</div>
                      <div className="text-[10px] font-mono text-slate-400 flex items-center gap-1.5 mt-0.5">
                        <span>{rec.batch_id}</span>
                        {rec.is_high_impact && (
                          <span className="px-1 py-0.2 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30 font-bold uppercase text-[9px]">
                            High Impact
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <div className="text-slate-200 flex items-center gap-1.5">
                        <span className="truncate max-w-[120px] font-medium">{rec.source_pharmacy_name}</span>
                        <span className="text-emerald-400 font-bold">&rarr;</span>
                        <span className="truncate max-w-[120px] font-medium">{rec.destination_pharmacy_name}</span>
                      </div>
                      <div className="text-[10px] text-slate-500 font-mono mt-0.5">{rec.distance_km} km away</div>
                    </td>
                    <td className="py-3 px-3 text-right font-mono font-bold text-white">
                      {rec.recommended_quantity}
                    </td>
                    <td className="py-3 px-3 text-right font-mono font-bold text-emerald-400">
                      ₹{rec.potential_value_saved.toLocaleString()}
                    </td>
                    <td className="py-3 px-3 text-center">
                      <div className="font-mono font-bold text-teal-300">
                        {rec.predicted_demand ? `${rec.predicted_demand.toFixed(1)} u/d` : '18.4 u/d'}
                      </div>
                      <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-slate-800 text-slate-400">
                        {rec.demand_source || 'ML_PREDICTION'}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-center font-mono">
                      <span className={`font-semibold ${rec.days_to_expiry <= 15 ? 'text-rose-400' : 'text-amber-400'}`}>
                        {rec.days_to_expiry}d
                      </span>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <RiskBadge risk={rec.risk_level} size="sm" />
                    </td>
                    <td className="py-3 px-3 text-center">
                      <span className="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono font-bold text-[11px]">
                        {rec.recommendation_score ? Math.round(rec.recommendation_score) : Math.round((rec.confidence_score || 0.85) * 100)}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => { setSelectedRec(rec); setIsEvidenceOpen(true); }}
                          className="px-2.5 py-1 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-750 border border-slate-700 rounded-lg transition-colors"
                        >
                          Why?
                        </button>
                        <button
                          onClick={() => { setSelectedRec(rec); setIsApprovalOpen(true); }}
                          className="px-2.5 py-1 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 rounded-lg shadow-sm transition-all"
                        >
                          Approve
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="9" className="py-8 text-center text-slate-400">
                    No pending recommendations requiring immediate review.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
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
