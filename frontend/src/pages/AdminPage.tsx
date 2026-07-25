import React from 'react';
import { ShieldCheck, Database, Server, Cpu, FileSpreadsheet, Lock } from 'lucide-react';

export const AdminPage: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-gov-navy-900 text-white p-6 rounded-2xl shadow-md border border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-gov-saffron-600 flex items-center justify-center shadow">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold">JanSathi Portal Admin</h1>
              <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700 font-mono">
                PLACEHOLDER
              </span>
            </div>
            <p className="text-xs text-slate-400">System Monitoring, Knowledge Base Administration & Services Overview</p>
          </div>
        </div>
      </div>

      {/* Admin Grid Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="gov-card p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase">FastAPI Server</span>
            <Server className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-xl font-extrabold text-slate-900">Active</p>
          <p className="text-[11px] text-emerald-700 font-medium">GET /health responding</p>
        </div>

        <div className="gov-card p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase">Database Engine</span>
            <Database className="w-4 h-4 text-gov-saffron-600" />
          </div>
          <p className="text-xl font-extrabold text-slate-900">SQLite</p>
          <p className="text-[11px] text-slate-500">jansathi.db configured</p>
        </div>

        <div className="gov-card p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase">API Services</span>
            <Cpu className="w-4 h-4 text-blue-600" />
          </div>
          <p className="text-xl font-extrabold text-slate-900">4 Modules</p>
          <p className="text-[11px] text-slate-500">Routers, Services, Models, Utils</p>
        </div>

        <div className="gov-card p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase">Knowledge Base</span>
            <FileSpreadsheet className="w-4 h-4 text-purple-600" />
          </div>
          <p className="text-xl font-extrabold text-slate-900">Ready</p>
          <p className="text-[11px] text-slate-500">Scheme document indexing ready</p>
        </div>
      </div>

      {/* Admin Control Shell Notice */}
      <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-500 mx-auto flex items-center justify-center">
          <Lock className="w-6 h-6" />
        </div>
        <div className="max-w-md mx-auto space-y-1">
          <h2 className="text-base font-bold text-slate-900">Admin Control Panel Shell</h2>
          <p className="text-xs text-slate-500">
            This module is reserved for portal administrators to manage public service schemes, monitor request analytics, and configure system rules.
          </p>
        </div>
      </div>
    </div>
  );
};
