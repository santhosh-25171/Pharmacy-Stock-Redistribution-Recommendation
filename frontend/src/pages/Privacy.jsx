import React, { useState } from 'react';
import { Lock, ShieldCheck, CheckCircle2, UserCheck, AlertCircle, FileText } from 'lucide-react';

export const Privacy = () => {
  const [acknowledged, setAcknowledged] = useState(
    localStorage.getItem('privacy_acknowledged') === 'true'
  );

  const handleToggleAcknowledge = () => {
    const next = !acknowledged;
    setAcknowledged(next);
    localStorage.setItem('privacy_acknowledged', next ? 'true' : 'false');
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-2">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Lock className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-black text-white tracking-tight">Privacy, Data Governance & Consent Center</h1>
            <p className="text-xs text-slate-400 mt-0.5">Synthetic Data Framework & Role-Based Access Transparency</p>
          </div>
        </div>
      </div>

      {/* Prominent Synthetic Data Guarantee Banner */}
      <div className="p-5 rounded-2xl bg-emerald-950/30 border border-emerald-500/30 shadow-glow-emerald space-y-3">
        <div className="flex items-center gap-2.5 text-emerald-400 font-bold text-sm">
          <ShieldCheck className="w-5 h-5" />
          <span>100% Synthetic Operational Data Declaration</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          &ldquo;Synthetic operational pharmacy data is used exclusively for this prototype. No real patient names, patient identifiers, medical histories, prescription records, residential addresses, or any personally identifiable information (PII) are stored, processed, or transmitted by this application.&rdquo;
        </p>
      </div>

      {/* Structured Governance Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Card 1: What Data Is Used */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-3">
          <h3 className="font-bold text-sm text-white flex items-center gap-2">
            <FileText className="w-4 h-4 text-emerald-400" />
            1. Operational Data Categories Used
          </h3>
          <ul className="space-y-2 text-xs text-slate-300 list-disc list-inside leading-relaxed">
            <li><strong>Medicine Catalog:</strong> Generic chemical formulations, therapeutic classes, and unit pricing.</li>
            <li><strong>Synthetic Batches:</strong> Pseudorandom batch identifiers, remaining shelf lives, and stock quantities.</li>
            <li><strong>Aggregate Demand:</strong> Numerical daily/weekly dispensing velocity per branch.</li>
            <li><strong>Geographic Coordinates:</strong> Simulated metropolitan pharmacy hub coordinates for transit calculation.</li>
          </ul>
        </div>

        {/* Card 2: Role-Based Visibility Rules */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-3">
          <h3 className="font-bold text-sm text-white flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-emerald-400" />
            2. Role-Based Access Control (RBAC)
          </h3>
          <ul className="space-y-2 text-xs text-slate-300 leading-relaxed">
            <li><strong className="text-emerald-400">ADMIN:</strong> Unrestricted network-wide inventory, audit trail logs, and system configuration.</li>
            <li><strong className="text-blue-400">MANAGER:</strong> Supply chain analytics, network recommendation approvals, and simulation benchmarks.</li>
            <li><strong className="text-amber-400">PHARMACIST:</strong> Scoped strictly to assigned branch inventory and relevant transfer routes.</li>
          </ul>
        </div>
      </div>

      {/* Clinical Disclaimer */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-2">
        <h3 className="font-bold text-sm text-white flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-amber-400" />
          3. Clinical Safety & Scope Limitation
        </h3>
        <p className="text-xs text-slate-300 leading-relaxed">
          This system functions strictly as an operational logistics and supply-chain decision-support assistant. It does not diagnose conditions, prescribe medications, or replace pharmacist clinical judgment. All high-impact and high-value stock transfers require mandatory human verification before physical dispatch.
        </p>
      </div>

      {/* User Consent Acknowledgment Box */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg flex items-center justify-between gap-4">
        <div>
          <div className="font-bold text-sm text-white">Researcher / Operator Acknowledgment</div>
          <p className="text-xs text-slate-400 mt-0.5">
            Confirm understanding of synthetic data parameters and operational role guidelines.
          </p>
        </div>

        <button
          onClick={handleToggleAcknowledge}
          className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
            acknowledged
              ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-750 border border-slate-700'
          }`}
        >
          <CheckCircle2 className="w-4 h-4" />
          {acknowledged ? 'Consent Acknowledged' : 'Click to Acknowledge'}
        </button>
      </div>
    </div>
  );
};
