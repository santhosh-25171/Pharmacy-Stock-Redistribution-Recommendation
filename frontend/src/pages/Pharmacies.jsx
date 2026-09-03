import React, { useState, useEffect } from 'react';
import {
  Building2,
  MapPin,
  Truck,
  Boxes,
  AlertTriangle,
  RefreshCw,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { pharmacyService, recommendationService } from '../services/api';
import { NetworkMap } from '../components/NetworkMap';

export const Pharmacies = () => {
  const [pharmacies, setPharmacies] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedPharmacy, setSelectedPharmacy] = useState(null);
  const [pharmacyDetail, setPharmacyDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchPharmacies = async () => {
    setLoading(true);
    try {
      const [pharmData, recData] = await Promise.all([
        pharmacyService.getPharmacies(),
        recommendationService.getRecommendations(),
      ]);
      setPharmacies(pharmData);
      setRecommendations(recData);
      if (pharmData.length > 0 && !selectedPharmacy) {
        handleSelectPharmacy(pharmData[0]);
      }
    } catch (err) {
      console.error('Failed to load pharmacies:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPharmacy = async (pharm) => {
    setSelectedPharmacy(pharm);
    setDetailLoading(true);
    try {
      const detail = await pharmacyService.getPharmacyDetail(pharm.pharmacy_id);
      setPharmacyDetail(detail);
    } catch (err) {
      console.error('Failed to load pharmacy detail:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  useEffect(() => {
    fetchPharmacies();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
        <div>
          <div className="flex items-center gap-2.5">
            <Building2 className="w-6 h-6 text-emerald-400" />
            <h1 className="text-xl font-black text-white tracking-tight">Pharmacy Network & Capacity Hub</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Geographic hub monitoring, storage utilization, and inter-branch transfer connectivity across 18 locations.
          </p>
        </div>

        <button
          onClick={fetchPharmacies}
          className="px-3.5 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 flex items-center gap-2 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-emerald-400' : ''}`} /> Refresh Map & Nodes
        </button>
      </div>

      {/* Network Mesh Map */}
      <div className="space-y-2">
        <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Spatial Logistics Topology</h2>
        <NetworkMap
          pharmacies={pharmacies}
          recommendations={recommendations}
          onSelectPharmacy={handleSelectPharmacy}
        />
      </div>

      {/* Grid of Pharmacy Cards & Selected Detail Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pharmacy Cards (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            All Pharmacy Branches ({pharmacies.length})
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {pharmacies.map((p) => {
              const isSelected = selectedPharmacy?.pharmacy_id === p.pharmacy_id;
              const isClosed = p.operating_status === 'CLOSED';
              const isMaint = p.operating_status === 'MAINTENANCE';

              return (
                <div
                  key={p.pharmacy_id}
                  onClick={() => handleSelectPharmacy(p)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-slate-850 border-emerald-500/50 shadow-glow-emerald'
                      : 'bg-slate-900 border-slate-800 hover:border-slate-700 hover:bg-slate-850/50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-[10px] font-mono text-emerald-400 font-bold">{p.pharmacy_id}</span>
                      <h3 className="font-bold text-sm text-white">{p.pharmacy_name}</h3>
                      <div className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-slate-500" /> {p.city}
                      </div>
                    </div>

                    <span
                      className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                        isClosed
                          ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                          : isMaint
                          ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                          : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      }`}
                    >
                      {p.operating_status}
                    </span>
                  </div>

                  <div className="mt-3 pt-3 border-t border-slate-800 flex justify-between text-xs">
                    <span className="text-slate-400">Storage Cap:</span>
                    <span className="font-mono text-white">{p.storage_capacity.toLocaleString()} units</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Pharmacy Detail Panel (1 col) */}
        <div className="space-y-4">
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Branch Details & Queues</h2>

          {selectedPharmacy && (
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
              {detailLoading ? (
                <div className="py-12 text-center text-slate-400 text-xs">
                  <RefreshCw className="w-6 h-6 text-emerald-400 animate-spin mx-auto mb-2" />
                  Loading branch inventory...
                </div>
              ) : pharmacyDetail ? (
                <>
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono text-emerald-400 font-bold">{pharmacyDetail.pharmacy_id}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold uppercase">
                        {pharmacyDetail.operating_status}
                      </span>
                    </div>
                    <h3 className="font-bold text-base text-white mt-1">{pharmacyDetail.pharmacy_name}</h3>
                    <p className="text-xs text-slate-400">{pharmacyDetail.city}</p>
                  </div>

                  {/* Metrics list */}
                  <div className="space-y-2 text-xs">
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center">
                      <span className="text-slate-400">Total Stock Value</span>
                      <span className="font-bold font-mono text-white">₹{pharmacyDetail.total_stock_value.toLocaleString()}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center">
                      <span className="text-slate-400">Near-Expiry Value</span>
                      <span className="font-bold font-mono text-amber-400">₹{pharmacyDetail.near_expiry_value.toLocaleString()}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center">
                      <span className="text-slate-400">Near-Expiry Batches</span>
                      <span className="font-bold font-mono text-rose-400">{pharmacyDetail.near_expiry_count} batches</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center">
                      <span className="text-slate-400">Outgoing Transfer Queue</span>
                      <span className="font-bold font-mono text-emerald-400">{pharmacyDetail.outgoing_transfers_count} transfers</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center">
                      <span className="text-slate-400">Incoming Transfer Queue</span>
                      <span className="font-bold font-mono text-blue-400">{pharmacyDetail.incoming_transfers_count} transfers</span>
                    </div>
                  </div>

                  {/* Storage Capacity meter */}
                  <div className="space-y-1.5 pt-2 border-t border-slate-800">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-400">Storage Utilization</span>
                      <span className="font-mono text-slate-200 font-bold">~60% Utilized</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                      <div className="h-full bg-emerald-500 rounded-full w-[60%]"></div>
                    </div>
                  </div>
                </>
              ) : null}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
