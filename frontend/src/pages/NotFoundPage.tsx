import React from 'react';
import { NavLink } from 'react-router-dom';
import { ArrowLeft, AlertCircle } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="max-w-md mx-auto my-12 text-center bg-white p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
      <div className="w-16 h-16 rounded-full bg-gov-saffron-50 text-gov-saffron-600 mx-auto flex items-center justify-center border border-gov-saffron-100">
        <AlertCircle className="w-8 h-8" />
      </div>

      <div className="space-y-2">
        <span className="text-4xl font-extrabold text-gov-navy-900 tracking-tight">404</span>
        <h1 className="text-lg font-bold text-slate-900">Page Not Found</h1>
        <p className="text-xs text-slate-500 leading-relaxed">
          The public service page or resource you are looking for could not be located.
        </p>
      </div>

      <div className="pt-4 border-t border-slate-100">
        <NavLink
          to="/"
          className="inline-flex items-center space-x-2 px-5 py-2.5 bg-gov-navy-800 hover:bg-gov-navy-900 text-white rounded-xl text-xs font-semibold shadow transition-colors focus-ring"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Portal Home</span>
        </NavLink>
      </div>
    </div>
  );
};
