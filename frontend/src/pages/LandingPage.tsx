import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  MessageSquare, 
  BellRing, 
  FileText, 
  HelpCircle, 
  ShieldCheck, 
  ArrowRight, 
  Users, 
  PhoneCall, 
  Languages 
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const serviceCards = [
    {
      title: 'AI Public Assistance',
      description: 'Get instant answers about government welfare schemes, application procedures, and eligibility.',
      icon: MessageSquare,
      link: '/chat',
      badge: 'AI Powered',
      color: 'from-amber-500 to-gov-saffron-600',
    },
    {
      title: 'Citizen Reminders',
      description: 'Set alerts for pension verifications, utility bill due dates, and civic document renewals.',
      icon: BellRing,
      link: '/reminders',
      badge: 'Automated',
      color: 'from-blue-600 to-gov-navy-800',
    },
    {
      title: 'Scheme Guidance',
      description: 'Explore step-by-step guides for ration card updates, PM-Kisan, Ayushman Bharat, and housing schemes.',
      icon: FileText,
      link: '/chat',
      badge: 'Verified Info',
      color: 'from-emerald-600 to-gov-green-700',
    },
    {
      title: 'Portal Admin',
      description: 'Manage knowledge bases, monitor user queries, and manage citizen support configurations.',
      icon: ShieldCheck,
      link: '/admin',
      badge: 'Internal',
      color: 'from-slate-700 to-slate-900',
    },
  ];

  const highlights = [
    { icon: Languages, title: 'Multilingual Ready', desc: 'Designed to support regional Indian languages.' },
    { icon: Users, title: 'Citizen-First Design', desc: 'Simple, high-contrast, accessible UI for all age groups.' },
    { icon: PhoneCall, title: 'Omnichannel Vision', desc: 'Prepared for web, mobile, and WhatsApp integrations.' },
  ];

  return (
    <div className="space-y-10">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-gov-navy-900 via-gov-navy-800 to-slate-900 text-white rounded-2xl p-6 sm:p-10 shadow-xl border border-slate-800">
        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-gov-saffron-600/30 border border-gov-saffron-500/50 text-gov-saffron-100 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-gov-saffron-500 animate-pulse" />
            <span>Empowering Public Service Access</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight leading-tight">
            Your Trusted AI Companion for <span className="text-gov-saffron-500">Citizen Services</span>
          </h1>

          <p className="text-slate-300 text-base sm:text-lg leading-relaxed">
            JanSathi AI connects citizens directly with reliable guidance on government welfare programs, document applications, and civic reminders.
          </p>

          <div className="flex flex-wrap gap-4 pt-2">
            <NavLink
              to="/chat"
              className="inline-flex items-center space-x-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-gov-saffron-500 to-gov-saffron-600 hover:from-gov-saffron-600 hover:to-gov-saffron-700 text-white font-bold shadow-lg hover:shadow-gov-saffron-600/40 hover:scale-[1.02] transition-all focus-ring"
            >
              <MessageSquare className="w-5 h-5" />
              <span>Start Chat</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </NavLink>

            <NavLink
              to="/reminders"
              className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-gov-navy-800 hover:bg-gov-navy-700 text-slate-100 font-semibold border border-slate-700 transition-all focus-ring"
            >
              <BellRing className="w-5 h-5" />
              <span>View Reminders</span>
            </NavLink>
          </div>
        </div>

        {/* Decorative background element */}
        <div className="absolute -right-16 -bottom-16 w-80 h-80 bg-gov-saffron-600/10 rounded-full blur-3xl pointer-events-none" />
      </section>

      {/* Quick Service Cards */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Public Service Portals</h2>
            <p className="text-xs text-slate-500">Quick access to essential JanSathi modules</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {serviceCards.map((card, index) => {
            const Icon = card.icon;
            return (
              <div
                key={index}
                className="gov-card p-5 flex flex-col justify-between group hover:-translate-y-1 transition-all"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${card.color} text-white flex items-center justify-center shadow-md`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                      {card.badge}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-900 mb-1 group-hover:text-gov-saffron-600 transition-colors">
                    {card.title}
                  </h3>
                  <p className="text-xs text-slate-600 leading-relaxed mb-4">
                    {card.description}
                  </p>
                </div>

                <NavLink
                  to={card.link}
                  className="inline-flex items-center text-xs font-semibold text-gov-navy-800 group-hover:text-gov-saffron-600 transition-colors pt-2 border-t border-slate-100"
                >
                  <span>Access Module</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1 transition-transform group-hover:translate-x-1" />
                </NavLink>
              </div>
            );
          })}
        </div>
      </section>

      {/* Accessibility & Design Highlights */}
      <section className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl font-bold text-slate-900">Designed for Every Citizen</h2>
          <p className="text-xs sm:text-sm text-slate-600">
            JanSathi AI is built with accessibility, speed, and trust as foundational pillars.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
          {highlights.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div key={idx} className="flex items-start space-x-4 p-4 rounded-xl bg-gov-ash border border-slate-200/60">
                <div className="w-10 h-10 rounded-lg bg-gov-saffron-100 text-gov-saffron-700 flex items-center justify-center shrink-0">
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 mb-0.5">{item.title}</h3>
                  <p className="text-xs text-slate-600">{item.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Info Callout */}
      <section className="bg-gov-green-50 border border-gov-green-100 rounded-xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-gov-green-600 text-white flex items-center justify-center shrink-0">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-gov-green-700">Project Foundation Status</h4>
            <p className="text-xs text-slate-700">
              The project structure, routes, FastAPI endpoints, and database connection are configured and ready for business logic.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
