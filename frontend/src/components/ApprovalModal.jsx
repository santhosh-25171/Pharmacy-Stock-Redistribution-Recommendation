import React, { useState } from 'react';
import { X, CheckCircle2, AlertTriangle, ShieldAlert } from 'lucide-react';

export const ApprovalModal = ({ recommendation, isOpen, onClose, onConfirm }) => {
  const [notes, setNotes] = useState('');
  const [confirmedHighImpact, setConfirmedHighImpact] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen || !recommendation) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (recommendation.is_high_impact && !confirmedHighImpact) return;
    
    setIsSubmitting(true);
    try {
      await onConfirm({
        notes: notes.trim() || 'Approved by authorized pharmacist/manager',
        confirmed_high_impact: confirmedHighImpact,
      });
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-800 bg-slate-850">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Authorize Stock Transfer</h3>
              <p className="text-xs text-slate-400">{recommendation.recommendation_id}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1.5">
            <div className="flex justify-between">
              <span className="text-slate-400">Medicine:</span>
              <span className="font-semibold text-white">{recommendation.medicine_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Quantity:</span>
              <span className="font-semibold text-emerald-400">{recommendation.recommended_quantity} units</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Route:</span>
              <span className="text-slate-300 font-mono text-[11px] truncate max-w-[200px]">
                {recommendation.source_pharmacy_id} → {recommendation.destination_pharmacy_id}
              </span>
            </div>
            <div className="flex justify-between border-t border-slate-800/80 pt-1.5">
              <span className="text-slate-400">Value Protected:</span>
              <span className="font-bold text-emerald-400">₹{recommendation.potential_value_saved.toLocaleString()}</span>
            </div>
          </div>

          {/* High Impact Checkbox */}
          {recommendation.is_high_impact && (
            <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-2">
              <div className="flex items-center gap-2 text-amber-300 text-xs font-bold">
                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                <span>High-Impact Action Confirmation Required</span>
              </div>
              <label className="flex items-start gap-2.5 cursor-pointer text-xs text-slate-200">
                <input
                  type="checkbox"
                  checked={confirmedHighImpact}
                  onChange={(e) => setConfirmedHighImpact(e.target.checked)}
                  className="mt-0.5 rounded border-slate-700 bg-slate-800 text-emerald-500 focus:ring-emerald-500 w-4 h-4"
                />
                <span>
                  I verify and approve the transfer of <strong className="text-white">{recommendation.recommended_quantity} units</strong> (₹{recommendation.potential_value_saved.toLocaleString()}) to {recommendation.destination_pharmacy_name}.
                </span>
              </label>
            </div>
          )}

          {/* Operational Notes */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Transfer Notes / Dispatch Instructions (Optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g., Courier dispatch arranged for morning transit."
              className="w-full h-20 px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 resize-none"
            />
          </div>

          {/* Buttons */}
          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-2 text-xs font-medium text-slate-400 hover:text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || (recommendation.is_high_impact && !confirmedHighImpact)}
              className="px-4 py-2 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-600/20 rounded-lg transition-all"
            >
              {isSubmitting ? 'Confirming...' : 'Approve & Log Action'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
