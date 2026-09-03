import React from 'react';
import { AlertTriangle, Flame, Clock, CheckCircle2, XCircle } from 'lucide-react';

export const RiskBadge = ({ risk, className = '', size = 'md' }) => {
  const normalized = (risk || '').toUpperCase();

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm',
  }[size] || 'px-2.5 py-1 text-xs';

  if (normalized === 'CRITICAL') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-rose-500/15 text-rose-400 border border-rose-500/30 ${sizeClasses} ${className}`}>
        <Flame className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
        <span>CRITICAL (≤ 7d)</span>
      </span>
    );
  }

  if (normalized === 'HIGH') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30 ${sizeClasses} ${className}`}>
        <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
        <span>HIGH (8-30d)</span>
      </span>
    );
  }

  if (normalized === 'MEDIUM') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-blue-500/15 text-blue-400 border border-blue-500/30 ${sizeClasses} ${className}`}>
        <Clock className="w-3.5 h-3.5 text-blue-400" />
        <span>MEDIUM (31-60d)</span>
      </span>
    );
  }

  if (normalized === 'LOW') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 ${sizeClasses} ${className}`}>
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
        <span>LOW (&gt;60d)</span>
      </span>
    );
  }

  if (normalized === 'EXPIRED') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-purple-500/15 text-purple-400 border border-purple-500/30 ${sizeClasses} ${className}`}>
        <XCircle className="w-3.5 h-3.5 text-purple-400" />
        <span>EXPIRED</span>
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center gap-1 font-medium rounded-full bg-slate-800 text-slate-300 border border-slate-700 ${sizeClasses} ${className}`}>
      {risk}
    </span>
  );
};
