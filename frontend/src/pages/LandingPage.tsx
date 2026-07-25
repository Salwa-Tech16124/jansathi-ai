import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  GraduationCap, 
  Tractor, 
  Heart, 
  UserCheck, 
  Stethoscope, 
  Home, 
  Briefcase, 
  Store, 
  Accessibility, 
  Baby,
  MessageSquare,
  ArrowRight,
  ShieldCheck,
  Zap,
  Sparkles
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const citizenCategories = [
    {
      title: 'Students',
      subtitle: 'Scholarships & Higher Education',
      icon: GraduationCap,
      emoji: '🎓',
      color: 'from-blue-600 to-indigo-700',
      badge: 'Scholarships',
      query: 'I am a Class 12 student seeking merit scholarship and education loan guidance',
    },
    {
      title: 'Farmers',
      subtitle: 'PM-Kisan, Fasal Bima & KCC',
      icon: Tractor,
      emoji: '👨‍🌾',
      color: 'from-emerald-600 to-green-700',
      badge: 'Agriculture',
      query: 'I cultivate wheat on 3 acres of land in Punjab and need crop support',
    },
    {
      title: 'Women Welfare',
      subtitle: 'Lakhpati Didi & PMMVY',
      icon: Heart,
      emoji: '👩',
      color: 'from-pink-500 to-rose-600',
      badge: 'Empowerment',
      query: 'I want to start a tailoring micro-business under Lakhpati Didi scheme',
    },
    {
      title: 'Senior Citizens',
      subtitle: 'Pensions & Health Cover',
      icon: UserCheck,
      emoji: '👴',
      color: 'from-amber-600 to-orange-700',
      badge: 'Pensions',
      query: 'I am 70 years old seeking senior citizen old age pension assistance',
    },
    {
      title: 'Healthcare',
      subtitle: 'Ayushman Bharat & Free Meds',
      icon: Stethoscope,
      emoji: '🏥',
      color: 'from-cyan-600 to-blue-700',
      badge: 'Health',
      query: 'My family needs medical treatment and cashless hospitalization cover',
    },
    {
      title: 'Housing',
      subtitle: 'PMAY Gramin & Urban Homes',
      icon: Home,
      emoji: '🏠',
      color: 'from-purple-600 to-indigo-800',
      badge: 'Housing',
      query: 'I need financial help to construct a pucca house under PMAY',
    },
    {
      title: 'Employment',
      subtitle: 'PMKVY & MGNREGA Work',
      icon: Briefcase,
      emoji: '💼',
      color: 'from-teal-600 to-emerald-800',
      badge: 'Skill & Jobs',
      query: 'I am an unemployed youth seeking skill training and guaranteed work',
    },
    {
      title: 'Business & MSME',
      subtitle: 'MUDRA & PMEGP Loans',
      icon: Store,
      emoji: '🏭',
      color: 'from-orange-500 to-amber-700',
      badge: 'Enterprise',
      query: 'I want to open a grocery shop under PM MUDRA loan scheme',
    },
    {
      title: 'Divyangjan',
      subtitle: 'Disability Pension & Aids',
      icon: Accessibility,
      emoji: '♿',
      color: 'from-indigo-600 to-blue-800',
      badge: 'Accessibility',
      query: 'I have a 60% disability certificate and seek financial aid and assistive devices',
    },
    {
      title: 'Child Welfare',
      subtitle: 'PM CARES & Nutrition',
      icon: Baby,
      emoji: '👶',
      color: 'from-rose-500 to-pink-700',
      badge: 'Protection',
      query: 'Looking for orphan child protection, foster care, and Anganwadi nutrition support',
    },
  ];

  const handleCategoryClick = (queryText: string) => {
    navigate('/chat', { state: { initialQuery: queryText } });
  };

  return (
    <div className="space-y-10">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-gov-navy-900 via-gov-navy-800 to-slate-900 text-white rounded-3xl p-6 sm:p-10 shadow-xl border border-slate-800">
        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-gov-saffron-600/30 border border-gov-saffron-500/50 text-gov-saffron-100 text-xs font-bold">
            <Sparkles className="w-4 h-4 text-gov-saffron-400 animate-pulse" />
            <span>AI-POWERED PUBLIC SERVICE ASSISTANCE</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight leading-tight">
            Government Schemes for <span className="text-gov-saffron-500">Every Citizen Group</span>
          </h1>

          <p className="text-slate-300 text-base sm:text-lg leading-relaxed">
            Select your citizen profile below or ask JanSathi AI to find eligible public welfare schemes, required documents, and set application deadline reminders.
          </p>

          <div className="flex flex-wrap gap-4 pt-2">
            <button
              onClick={() => navigate('/chat')}
              className="inline-flex items-center space-x-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-gov-saffron-500 to-gov-saffron-600 hover:from-gov-saffron-600 hover:to-gov-saffron-700 text-white font-bold shadow-lg hover:shadow-gov-saffron-600/40 hover:scale-[1.02] transition-all focus:ring-2 focus:ring-amber-500 focus:outline-none"
            >
              <MessageSquare className="w-5 h-5" />
              <span>Start AI Case Worker Chat</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>
          </div>
        </div>

        {/* Decorative blur elements */}
        <div className="absolute -right-16 -bottom-16 w-80 h-80 bg-gov-saffron-600/10 rounded-full blur-3xl pointer-events-none" />
      </section>

      {/* 10 Citizen Group Category Cards Grid */}
      <section className="space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <span>Select Your Citizen Category</span>
              <span className="text-xs bg-gov-saffron-100 text-gov-saffron-800 px-2.5 py-0.5 rounded-full font-bold border border-gov-saffron-200">
                10 GROUPS
              </span>
            </h2>
            <p className="text-xs text-slate-500">Click any card to start a tailored AI consultation</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {citizenCategories.map((cat, idx) => {
            const Icon = cat.icon;
            return (
              <button
                key={idx}
                onClick={() => handleCategoryClick(cat.query)}
                className="gov-card p-5 text-left flex flex-col justify-between group hover:-translate-y-1 hover:border-gov-saffron-400 transition-all focus:ring-2 focus:ring-amber-500 focus:outline-none cursor-pointer bg-white border border-slate-200/90 rounded-2xl shadow-xs"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${cat.color} text-white flex items-center justify-center shadow-sm`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                      {cat.badge}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-slate-900 mb-1 group-hover:text-gov-saffron-600 transition-colors flex items-center gap-1.5">
                    <span>{cat.emoji}</span>
                    <span>{cat.title}</span>
                  </h3>
                  <p className="text-xs text-slate-500 leading-snug mb-4">
                    {cat.subtitle}
                  </p>
                </div>

                <div className="inline-flex items-center text-xs font-semibold text-gov-saffron-700 group-hover:text-gov-saffron-800 transition-colors pt-2.5 border-t border-slate-100 w-full justify-between">
                  <span>Explore Schemes</span>
                  <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
                </div>
              </button>
            );
          })}
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl font-bold text-slate-900">How JanSathi AI Serves Citizens</h2>
          <p className="text-xs sm:text-sm text-slate-600">
            Smart entity extraction, category classification, and official SQLite scheme database grounding.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
          <div className="flex items-start space-x-4 p-4 rounded-xl bg-gov-ash border border-slate-200/60">
            <div className="w-10 h-10 rounded-lg bg-gov-saffron-100 text-gov-saffron-700 flex items-center justify-center shrink-0">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 mb-0.5">Category Classification</h3>
              <p className="text-xs text-slate-600">Automatically routes queries to targeted scheme databases.</p>
            </div>
          </div>

          <div className="flex items-start space-x-4 p-4 rounded-xl bg-gov-ash border border-slate-200/60">
            <div className="w-10 h-10 rounded-lg bg-gov-saffron-100 text-gov-saffron-700 flex items-center justify-center shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 mb-0.5">Zero Hallucination</h3>
              <p className="text-xs text-slate-600">Sarvam AI reasons strictly over official government records.</p>
            </div>
          </div>

          <div className="flex items-start space-x-4 p-4 rounded-xl bg-gov-ash border border-slate-200/60">
            <div className="w-10 h-10 rounded-lg bg-gov-saffron-100 text-gov-saffron-700 flex items-center justify-center shrink-0">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 mb-0.5">Omnichannel Access</h3>
              <p className="text-xs text-slate-600">Accessible over Web, Mobile, and WhatsApp Sandbox.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
