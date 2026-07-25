import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { MessageSquareText, BellRing, ShieldCheck, Home, Menu, X, Landmark, Activity } from 'lucide-react';
import { checkHealth } from '../services/api';

export const Navbar: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    const verifyHealth = async () => {
      const res = await checkHealth();
      setIsBackendHealthy(res.status === 'ok');
    };
    verifyHealth();
  }, []);

  const navLinks = [
    { to: '/', label: 'Home', icon: Home },
    { to: '/chat', label: 'AI Assistant', icon: MessageSquareText },
    { to: '/reminders', label: 'Reminders', icon: BellRing },
    { to: '/admin', label: 'Admin Portal', icon: ShieldCheck },
  ];

  return (
    <header className="sticky top-0 z-50 bg-gov-navy-900 text-white shadow-lg border-b border-gov-navy-800">
      {/* Top Tricolor Accent Line */}
      <div className="tricolor-stripe" />

      {/* Top Banner Bar */}
      <div className="bg-gov-navy-800/80 text-slate-300 text-xs px-4 py-1.5 border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="inline-block px-1.5 py-0.5 text-[10px] font-semibold bg-gov-saffron-600 text-white rounded">
              OFFICIAL DEMO
            </span>
            <span className="hidden sm:inline">JanSathi AI Citizen Public Service Assistance Portal</span>
            <span className="sm:hidden">JanSathi AI Citizen Portal</span>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1.5 text-[11px]" title="FastAPI Backend Health Status">
              <Activity className="w-3.5 h-3.5 text-slate-400" />
              <span>Backend:</span>
              {isBackendHealthy === null ? (
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
              ) : isBackendHealthy ? (
                <span className="flex items-center space-x-1 text-emerald-400 font-medium">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span>Online</span>
                </span>
              ) : (
                <span className="flex items-center space-x-1 text-rose-400 font-medium">
                  <span className="w-2 h-2 rounded-full bg-rose-500" />
                  <span>Offline</span>
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Navbar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo Brand */}
          <NavLink to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-gov-saffron-500 to-gov-saffron-700 flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
              <Landmark className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="text-xl font-bold tracking-tight text-white group-hover:text-gov-saffron-100 transition-colors">
                  JanSathi <span className="text-gov-saffron-500 font-extrabold">AI</span>
                </span>
              </div>
              <p className="text-[11px] text-slate-300 font-medium">जनसाथी • Empowering Every Citizen</p>
            </div>
          </NavLink>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-gov-saffron-600 text-white shadow'
                        : 'text-slate-200 hover:bg-gov-navy-800 hover:text-white'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{link.label}</span>
                </NavLink>
              );
            })}
          </nav>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-gov-navy-800 focus:outline-none focus:ring-2 focus:ring-gov-saffron-500"
              aria-label="Toggle Navigation Menu"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-gov-navy-900 border-b border-gov-navy-800 px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                onClick={() => setIsMobileMenuOpen(false)}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-base font-medium transition-colors ${
                    isActive
                      ? 'bg-gov-saffron-600 text-white'
                      : 'text-slate-200 hover:bg-gov-navy-800 hover:text-white'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span>{link.label}</span>
              </NavLink>
            );
          })}
        </div>
      )}
    </header>
  );
};
