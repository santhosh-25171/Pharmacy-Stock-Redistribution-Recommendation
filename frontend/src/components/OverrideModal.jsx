import React, { useState } from 'react';
import { X, Sliders, IndianRupee } from 'lucide-react';

const OVERRIDE_REASONS = [
  'Adjusted based on physical batch count',
  'Partial shipment requested by destination',
  'Manager operational decision',
  'Local safety stock buffer increase',
  'Transfer vehicle space limitation',
  'Other'
];

export const OverrideModal = ({ recommendation, isOpen, onClose, onConfirm }) => {
  const [overrideQty, setOverrideQty] = useState(recommendation?.recommended_quantity || 10);
  const [reasonCategory, setReasonCategory] = useState(OVERRIDE_REASONS[0]);
  const [customReason, setCustomReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  React.useEffect(() => {
    if (isOpen && recommendation) {
      setOverrideQty(recommendation.recommended_quantity || 10);
      setReasonCategory(OVERRIDE_REASONS[0]);
      setCustomReason('');
      setIsSubmitting(false);
    }
  }, [isOpen, recommendation]);

  if (!isOpen || !recommendation) return null;

  const recalculatedValue = Math.round(overrideQty * recommendation.unit_price);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (overrideQty <= 0 || !reasonCategory) return;

    setIsSubmitting(true);
    try {
      await onConfirm({
        overridden_quantity: parseInt(overrideQty, 10),
        reason_category: reasonCategory,
        custom_reason: customReason.trim() || undefined,
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
            <div className="p-2 rounded-lg bg-amber-500/15 text-amber-400 border border-amber-500/30">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Override Transfer Quantity</h3>
              <p className="text-xs text-slate-400">{recommendation.recommendation_id}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-400">Medicine:</span>
              <span className="font-semibold text-white truncate max-w-[200px]">{recommendation.medicine_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Original Recommended:</span>
              <span className="text-slate-300 font-mono">{recommendation.recommended_quantity} units</span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              New Transfer Quantity (Units) <span className="text-amber-400">*</span>
            </label>
            <input
              type="number"
              min="1"
              max="1000"
              value={overrideQty}
              onChange={(e) => setOverrideQty(Math.max(1, parseInt(e.target.value) || 1))}
              className="w-full px-3 py-2 text-sm font-bold bg-slate-950 border border-slate-800 rounded-xl text-amber-400 focus:outline-none focus:border-amber-500"
            />
            <div className="flex justify-between items-center mt-1.5 text-xs">
              <span className="text-slate-400">New Value Protected:</span>
              <span className="font-bold text-emerald-400">₹{recalculatedValue.toLocaleString()}</span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Override Justification <span className="text-amber-400">*</span>
            </label>
            <select
              value={reasonCategory}
              onChange={(e) => setReasonCategory(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-amber-500"
            >
              {OVERRIDE_REASONS.map((reason) => (
                <option key={reason} value={reason}>
                  {reason}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Detailed Notes (Optional)
            </label>
            <textarea
              value={customReason}
              onChange={(e) => setCustomReason(e.target.value)}
              placeholder="Explain why the transfer quantity was modified..."
              className="w-full h-18 px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 resize-none"
            />
          </div>

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
              disabled={isSubmitting || overrideQty <= 0}
              className="px-4 py-2 text-xs font-semibold text-white bg-amber-600 hover:bg-amber-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-amber-600/20 rounded-lg transition-all"
            >
              {isSubmitting ? 'Applying...' : 'Apply Quantity Override'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
