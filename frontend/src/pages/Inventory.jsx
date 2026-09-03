import React, { useState, useEffect } from 'react';
import {
  Boxes,
  Search,
  Filter,
  RefreshCw,
  Building2,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Calendar,
  Sparkles,
} from 'lucide-react';
import { inventoryService, pharmacyService } from '../services/api';
import { RiskBadge } from '../components/RiskBadge';

export const Inventory = ({ onSelectRecommendation }) => {
  const [inventory, setInventory] = useState([]);
  const [pharmacies, setPharmacies] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filter states
  const [search, setSearch] = useState('');
  const [selectedPharmacy, setSelectedPharmacy] = useState('');
  const [selectedRisk, setSelectedRisk] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');

  // Pagination states
  const [page, setPage] = useState(1);
  const pageSize = 25;

  const fetchInventory = async () => {
    setLoading(true);
    try {
      const params = {
        limit: 500,
        search: search.trim() || undefined,
        pharmacy_id: selectedPharmacy || undefined,
        risk_level: selectedRisk || undefined,
        category: selectedCategory || undefined,
        stock_status: selectedStatus || undefined,
      };
      const [invData, pharmData] = await Promise.all([
        inventoryService.getInventory(params),
        pharmacies.length === 0 ? pharmacyService.getPharmacies() : Promise.resolve(pharmacies),
      ]);
      setInventory(invData);
      if (pharmacies.length === 0) setPharmacies(pharmData);
    } catch (err) {
      console.error('Failed to fetch inventory:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInventory();
  }, [selectedPharmacy, selectedRisk, selectedCategory, selectedStatus]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchInventory();
  };

  const paginatedItems = inventory.slice((page - 1) * pageSize, page * pageSize);
  const totalPages = Math.ceil(inventory.length / pageSize) || 1;

  // Categories list
  const categories = [
    'All Categories',
    'Antibiotic',
    'Cardiovascular',
    'Antidiabetic',
    'Analgesic',
    'Respiratory',
    'Gastrointestinal',
    'Steroid',
    'Antihistamine',
    'Critical Care',
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
        <div>
          <div className="flex items-center gap-2.5">
            <Boxes className="w-6 h-6 text-emerald-400" />
            <h1 className="text-xl font-black text-white tracking-tight">Pharmacy Network Inventory Monitor</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time batch shelf-life analytics, localized consumption velocity, and excess stock tracking across 5,000+ records.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-slate-300 font-mono">
            {inventory.length} Batches Loaded
          </span>
          <button
            onClick={fetchInventory}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 transition-colors"
            title="Refresh Inventory"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-emerald-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3">
          {/* Search bar */}
          <div className="flex-1 relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search medicine name, category or batch code..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          {/* Pharmacy Filter */}
          <select
            value={selectedPharmacy}
            onChange={(e) => { setSelectedPharmacy(e.target.value); setPage(1); }}
            className="px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Pharmacies</option>
            {pharmacies.map((p) => (
              <option key={p.pharmacy_id} value={p.pharmacy_id}>
                {p.pharmacy_id} - {p.pharmacy_name}
              </option>
            ))}
          </select>

          {/* Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => { setSelectedCategory(e.target.value === 'All Categories' ? '' : e.target.value); setPage(1); }}
            className="px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>

          {/* Risk Filter */}
          <select
            value={selectedRisk}
            onChange={(e) => { setSelectedRisk(e.target.value); setPage(1); }}
            className="px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Risk Levels</option>
            <option value="CRITICAL">Critical (≤ 7 days)</option>
            <option value="HIGH">High (8-30 days)</option>
            <option value="MEDIUM">Medium (31-60 days)</option>
            <option value="LOW">Low (&gt; 60 days)</option>
            <option value="EXPIRED">Expired</option>
          </select>

          {/* Filter Submit Button */}
          <button
            type="submit"
            className="px-4 py-2 text-xs font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-600/20 transition-all flex items-center justify-center gap-1.5"
          >
            <Filter className="w-3.5 h-3.5" /> Filter
          </button>
        </form>
      </div>

      {/* Inventory Table */}
      <div className="rounded-2xl bg-slate-900 border border-slate-800 shadow-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-850/60 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-4">Medicine & Category</th>
                <th className="py-3 px-4">Batch / Pharmacy</th>
                <th className="py-3 px-4 text-right">Quantity</th>
                <th className="py-3 px-4 text-right">Stock Value</th>
                <th className="py-3 px-4">Expiry Date</th>
                <th className="py-3 px-4">Risk Status</th>
                <th className="py-3 px-4 text-right">Daily Velocity</th>
                <th className="py-3 px-4 text-right">Excess Qty</th>
                <th className="py-3 px-4">Action Recommendation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-xs">
              {loading ? (
                <tr>
                  <td colSpan="9" className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 text-emerald-400 animate-spin mx-auto mb-2" />
                    Filtering batch inventory...
                  </td>
                </tr>
              ) : paginatedItems.length > 0 ? (
                paginatedItems.map((b) => (
                  <tr key={b.inventory_id} className="hover:bg-slate-850/50 transition-colors">
                    <td className="py-3 px-4">
                      <div className="font-bold text-white">{b.medicine_name}</div>
                      <span className="text-[10px] text-slate-400">{b.medicine_category}</span>
                    </td>

                    <td className="py-3 px-4 font-mono text-[11px]">
                      <div className="text-slate-300 font-semibold">{b.batch_id}</div>
                      <div className="text-slate-500">{b.pharmacy_name}</div>
                    </td>

                    <td className="py-3 px-4 text-right font-mono font-bold text-slate-200">
                      {b.quantity}
                    </td>

                    <td className="py-3 px-4 text-right font-mono font-bold text-emerald-400">
                      ₹{b.total_value.toLocaleString()}
                    </td>

                    <td className="py-3 px-4">
                      <div className="font-mono text-slate-300">{b.expiry_date}</div>
                      <div className="text-[10px] text-slate-500">{b.days_to_expiry} days remaining</div>
                    </td>

                    <td className="py-3 px-4">
                      <RiskBadge risk={b.risk_level} size="sm" />
                    </td>

                    <td className="py-3 px-4 text-right font-mono text-slate-300">
                      {b.daily_demand} / day
                    </td>

                    <td className="py-3 px-4 text-right">
                      {b.excess_quantity > 0 ? (
                        <span className="font-bold font-mono text-amber-400">+{b.excess_quantity}</span>
                      ) : (
                        <span className="text-slate-600 font-mono">0</span>
                      )}
                    </td>

                    <td className="py-3 px-4">
                      {b.recommended_action === 'REDISTRIBUTE_EXCESS' ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
                          <Sparkles className="w-3 h-3" /> Redistribute
                        </span>
                      ) : b.recommended_action === 'DISPOSE_EXPIRED_BATCH' ? (
                        <span className="text-[11px] font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/30">
                          Dispose Expired
                        </span>
                      ) : (
                        <span className="text-[11px] text-slate-400">
                          {b.recommended_action.replace(/_/g, ' ')}
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="9" className="py-12 text-center text-slate-400">
                    No inventory records match the selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="flex items-center justify-between p-4 border-t border-slate-800 bg-slate-850/60 text-xs">
          <span className="text-slate-400">
            Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, inventory.length)} of {inventory.length} batches
          </span>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-200 border border-slate-700"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-slate-300 px-2">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-200 border border-slate-700"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
