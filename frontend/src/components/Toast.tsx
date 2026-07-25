import React, { useEffect } from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info';
  title: string;
  message?: string;
}

interface ToastProps {
  toast: ToastMessage | null;
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ toast, onClose }) => {
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => {
      onClose();
    }, 4000);
    return () => clearTimeout(timer);
  }, [toast, onClose]);

  if (!toast) return null;

  const bgColors = {
    success: 'bg-emerald-900/95 border-emerald-500 text-white',
    error: 'bg-rose-900/95 border-rose-500 text-white',
    info: 'bg-gov-navy-900/95 border-gov-saffron-500 text-white',
  };

  const icons = {
    success: <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />,
    error: <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />,
    info: <Info className="w-5 h-5 text-gov-saffron-400 shrink-0" />,
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 max-w-md w-full animate-in fade-in slide-in-from-bottom-5 duration-300">
      <div
        className={`flex items-start justify-between gap-3 p-4 rounded-2xl border shadow-xl backdrop-blur-md ${bgColors[toast.type]}`}
      >
        <div className="flex items-start space-x-3">
          {icons[toast.type]}
          <div>
            <h4 className="text-xs sm:text-sm font-bold">{toast.title}</h4>
            {toast.message && <p className="text-xs text-slate-200 mt-0.5 leading-relaxed">{toast.message}</p>}
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-white/10 text-slate-300 hover:text-white transition-colors"
          aria-label="Close notification"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
