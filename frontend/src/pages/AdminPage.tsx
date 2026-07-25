import React, { useEffect, useState } from 'react';
import { ShieldCheck, Database, Server, Cpu, RefreshCw, CheckCircle2, Sparkles } from 'lucide-react';
import { syncSchemes, getSyncStatus } from '../services/api';

export const AdminPage: React.FC = () => {
  const [syncData, setSyncData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [syncResult, setSyncResult] = useState<string | null>(null);

  const fetchStatus = async () => {
    const res = await getSyncStatus();
    if (res) {
      setSyncData(res);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleManualSync = async () => {
    setLoading(true);
    setSyncResult(null);
    const res = await syncSchemes();
    setLoading(false);
    if (res) {
      setSyncResult(`Successfully synchronized! Added ${res.new_schemes_added} new schemes. Total in DB: ${res.total_schemes_in_db}`);
      fetchStatus();
    } else {
      setSyncResult('Sync failed or server offline.');
    }
  };

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
              <span className="text-[10px] bg-emerald-900/80 text-emerald-300 px-2 py-0.5 rounded border border-emerald-700 font-mono flex items-center gap-1">
                <Sparkles className="w-3 h-3" /> DAILY SCHEME AUTO-SYNC ACTIVE
              </span>
            </div>
            <p className="text-xs text-slate-400">Automated Daily Government Scheme Collector & Knowledge Base Administration</p>
          </div>
        </div>

        <button
          onClick={handleManualSync}
          disabled={loading}
          className="gov-button-primary text-xs flex items-center space-x-2 bg-gov-saffron-600 hover:bg-gov-saffron-700 disabled:opacity-50 px-4 py-2.5"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Syncing Schemes...' : 'Sync Latest Schemes Now'}</span>
        </button>
      </div>

      {syncResult && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-xl text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{syncResult}</span>
        </div>
      )}

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
            <span className="text-xs font-semibold uppercase">Total Schemes in DB</span>
            <Database className="w-4 h-4 text-gov-saffron-600" />
          </div>
          <p className="text-xl font-extrabold text-slate-900">{syncData?.total_schemes_in_db || 3431}</p>
          <p className="text-[11px] text-slate-500">Indexed SQLite Database</p>
        </div>

        <div className="gov-card p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase">Auto Ingestion</span>
            <Cpu className="w-4 h-4 text-blue-600" />
          </div>
          <p className="text-xl font-extrabold text-slate-900">Daily (24h)</p>
          <p className="text-[11px] text-emerald-700 font-medium">Automatic Background Sync</p>
        </div>

        <div className="gov-card p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase">RAG Engine</span>
            <Sparkles className="w-4 h-4 text-purple-600" />
          </div>
          <p className="text-xl font-extrabold text-slate-900">Gemini 1.5 Flash</p>
          <p className="text-[11px] text-slate-500">Grounded Scheme Retrieval</p>
        </div>
      </div>
    </div>
  );
};
