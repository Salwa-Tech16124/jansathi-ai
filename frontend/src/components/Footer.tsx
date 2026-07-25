import React from 'react';
import { Landmark, ShieldAlert, Heart, Globe, Mail } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-gov-navy-900 text-slate-300 border-t border-gov-navy-800 mt-auto">
      {/* Upper Footer: Quick Info */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <div className="w-8 h-8 rounded bg-gov-saffron-600 flex items-center justify-center text-white">
              <Landmark className="w-4 h-4" />
            </div>
            <span className="text-lg font-bold text-white">JanSathi AI</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            JanSathi AI is an accessible, multilingual public service platform built to simplify access to government schemes, civic updates, and citizen utilities.
          </p>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">Public Accessibility</h4>
          <ul className="text-xs space-y-2 text-slate-400">
            <li className="flex items-center space-x-2">
              <Globe className="w-3.5 h-3.5 text-gov-saffron-500" />
              <span>Multi-lingual Support Ready</span>
            </li>
            <li className="flex items-center space-x-2">
              <ShieldAlert className="w-3.5 h-3.5 text-gov-green-600" />
              <span>Voice & WhatsApp-First Architecture</span>
            </li>
            <li className="flex items-center space-x-2">
              <Mail className="w-3.5 h-3.5 text-gov-saffron-500" />
              <span>Open Citizen Helpline Integration</span>
            </li>
          </ul>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">Project Foundation</h4>
          <p className="text-xs text-slate-400 leading-relaxed mb-2">
            Built with React, Vite, TypeScript, Tailwind CSS, Python FastAPI, and SQLite database.
          </p>
          <span className="inline-block text-[10px] bg-gov-navy-800 text-slate-300 px-2 py-1 rounded border border-slate-700">
            Version 0.1.0 • Foundation Stage
          </span>
        </div>
      </div>

      {/* Bottom Tricolor Accent & Copyright */}
      <div className="bg-gov-navy-950 py-4 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-400 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>&copy; {new Date().getFullYear()} JanSathi AI. Designed for Public Welfare.</span>
          <span className="flex items-center space-x-1">
            <span>Crafted with</span>
            <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500 inline" />
            <span>for Citizens</span>
          </span>
        </div>
      </div>
      <div className="tricolor-stripe" />
    </footer>
  );
};
