import React from 'react';
import { Landmark, ShieldAlert, Heart, Globe, Cpu } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-gov-navy-900 text-slate-300 border-t border-gov-navy-800 mt-auto">
      {/* Upper Footer: Quick Info */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <div className="w-8 h-8 rounded-lg bg-gov-saffron-600 flex items-center justify-center text-white shadow">
              <Landmark className="w-4 h-4" />
            </div>
            <span className="text-lg font-bold text-white tracking-tight">JanSathi AI</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            JanSathi AI is an accessible, multilingual public service platform built to simplify access to government schemes, civic updates, and citizen utilities across 10 citizen groups.
          </p>
        </div>

        <div>
          <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Public Accessibility</h4>
          <ul className="text-xs space-y-2.5 text-slate-400">
            <li className="flex items-center space-x-2">
              <Globe className="w-3.5 h-3.5 text-gov-saffron-500" />
              <span>Multi-lingual Support Ready</span>
            </li>
            <li className="flex items-center space-x-2">
              <ShieldAlert className="w-3.5 h-3.5 text-emerald-400" />
              <span>Zero-Hallucination Database Grounding</span>
            </li>
            <li className="flex items-center space-x-2">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              <span>Twilio WhatsApp & Web AI Case Worker</span>
            </li>
          </ul>
        </div>

        <div>
          <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Powered By</h4>
          <div className="flex flex-wrap gap-2 text-[11px]">
            <span className="px-2.5 py-1 rounded-md bg-gov-navy-800 border border-slate-700 text-slate-200 font-medium">Sarvam AI</span>
            <span className="px-2.5 py-1 rounded-md bg-gov-navy-800 border border-slate-700 text-slate-200 font-medium">Twilio WhatsApp</span>
            <span className="px-2.5 py-1 rounded-md bg-gov-navy-800 border border-slate-700 text-slate-200 font-medium">FastAPI</span>
            <span className="px-2.5 py-1 rounded-md bg-gov-navy-800 border border-slate-700 text-slate-200 font-medium">React</span>
            <span className="px-2.5 py-1 rounded-md bg-gov-navy-800 border border-slate-700 text-slate-200 font-medium">SQLite</span>
          </div>
          <p className="text-[10px] text-slate-500 mt-3">Version 1.0.0 • Production Ready</p>
        </div>
      </div>

      {/* Bottom Tricolor Accent & Copyright */}
      <div className="bg-gov-navy-950 py-4 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-400 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>&copy; {new Date().getFullYear()} JanSathi AI. Designed for Public Welfare.</span>
          <span className="flex items-center space-x-1.5">
            <span>Powered by Sarvam AI • Twilio WhatsApp • FastAPI • React • SQLite</span>
            <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500 inline ml-1" />
          </span>
        </div>
      </div>
      <div className="tricolor-stripe" />
    </footer>
  );
};
