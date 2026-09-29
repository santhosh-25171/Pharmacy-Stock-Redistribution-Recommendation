import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log error internally for diagnostic purposes without leaking to user screen
    console.error(`[ErrorBoundary caught in ${this.props.sectionName || 'Section'}]:`, error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-rose-500/30 text-center max-w-xl mx-auto my-8 shadow-2xl backdrop-blur-md">
          <div className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center mx-auto mb-4 text-rose-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-white tracking-tight">
            Something went wrong while loading {this.props.sectionName || 'this section'}
          </h3>
          <p className="text-xs text-slate-400 mt-2 max-w-md mx-auto">
            An unexpected client error occurred in the operational view. The error has been isolated by the system error boundary to protect the rest of your session.
          </p>
          <div className="mt-6 flex items-center justify-center gap-3">
            <button
              onClick={this.handleRetry}
              className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-2 transition-all shadow-lg shadow-emerald-500/20"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry Section</span>
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition-all border border-slate-700"
            >
              Reload Application
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
