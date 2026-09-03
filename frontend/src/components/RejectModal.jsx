import React, { useState } from 'react';
import { X, XCircle, AlertCircle } from 'lucide-react';

const REJECTION_REASONS = [
  'Destination already received stock',
  'Physical stock count differs',
  'Transfer not operationally feasible',
  'Demand changed locally',
  'Manager operational decision',
  'Medicine packaging/quality concern',
  'Near-expiry local clearance prioritized',
  'Other'
];

export const RejectModal = ({ recommendation, isOpen, onClose, onConfirm }) => {
  const [reasonCategory, setReasonCategory] = useState(REJECTION_REASONS[0]);
  const [customReason, setCustomReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  React.useEffect(() => {
    if (isOpen) {
      setReasonCategory(REJECTION_REASONS[0]);
      setCustomReason('');
      setIsSubmitting(false);
    }
  }, [isOpen, recommendation]);

  if (!isOpen || !recommendation) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!reasonCategory) return;

    setIsSubmitting(true);
    try {
      await onConfirm({
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
            <div className="p-2 rounded-lg bg-rose-500/15 text-rose-400 border border-rose-500/30">
              <XCircle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Reject Transfer Recommendation</h3>
              <p className="text-xs text-slate-400">{recommendation.recommendation_id}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs flex items-center justify-between">
            <span className="text-slate-400">Medicine:</span>
            <span className="font-semibold text-white truncate max-w-[200px]">{recommendation.medicine_name}</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Reason for Rejection <span className="text-rose-400">*</span>
            </label>
            <select
              value={reasonCategory}
              onChange={(e) => setReasonCategory(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-rose-500"
            >
              {REJECTION_REASONS.map((reason) => (
                <option key={reason} value={reason}>
                  {reason}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Additional Details / Context {reasonCategory === 'Other' && <span className="text-rose-400">*</span>}
            </label>
            <textarea
              value={customReason}
              onChange={(e) => setCustomReason(e.target.value)}
              placeholder="Provide specific notes regarding why this transfer cannot proceed..."
              required={reasonCategory === 'Other'}
              className="w-full h-20 px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500 resize-none"
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
              disabled={isSubmitting || !reasonCategory || (reasonCategory === 'Other' && !customReason.trim())}
              className="px-4 py-2 text-xs font-semibold text-white bg-rose-600 hover:bg-rose-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-rose-600/20 rounded-lg transition-all"
            >
              {isSubmitting ? 'Recording...' : 'Reject & Record Reason'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
