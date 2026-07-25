import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  Landmark, 
  RefreshCw, 
  BellPlus, 
  Check, 
  Calendar, 
  FileText, 
  ShieldCheck, 
  AlertCircle,
  HelpCircle,
  ExternalLink
} from 'lucide-react';
import { sendAssistantChat, MatchedScheme, createReminder } from '../services/api';
import { Toast, ToastMessage } from '../components/Toast';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  time: string;
  matchedSchemes?: MatchedScheme[];
  missingFields?: string[];
  isError?: boolean;
}

export const ChatPage: React.FC = () => {
  const location = useLocation();
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [reminderCreatedIds, setReminderCreatedIds] = useState<number[]>([]);
  const [toast, setToast] = useState<ToastMessage | null>(null);

  const cleanText = (rawText: string): string => {
    return rawText.replace(/\*{1,2}/g, '');
  };
  
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'assistant',
      text: 'Namaste! I am JanSathi AI, your public assistance case worker.\n\nI can help citizens across 10 categories: Students 🎓, Farmers 👨‍🌾, Women 👩, Senior Citizens 👴, Health 🏥, Housing 🏠, Employment 💼, Business 🏭, Disability ♿, and Child Welfare 👶.\n\nHow may I assist you today?',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Multilingual Demo Prompts (Hindi, Hinglish, English) covering citizen categories
  const sampleQueries = [
    '🎓 मैं कक्षा 12 का छात्र हूँ, मुझे मेरिट छात्रवृत्ति चाहिए (Hindi)',
    '👨‍🌾 Mujhe PM Kisan aur kheti ke liye 3 acre zameen par madad chahiye (Hinglish)',
    '👩 main tailoring business kholna chahti hun Lakhpati Didi yojana me (Hinglish)',
    '👴 मेरी उम्र 70 वर्ष है, मुझे वृद्ध पेंशन योजना की जानकारी चाहिए (Hindi)',
    '🎓 I am a Class 12 student passed with 85% seeking merit scholarship',
    '👨‍🌾 I cultivate wheat on 3 acres of land in Punjab and need crop support',
    '🏥 Mere parivar ko Ayushman Bharat hospital treatment cover chahiye (Hinglish)',
    '♿ I have a 60% disability certificate and seek financial aid',
    '🏭 Mujhe grocery shop ke liye PM MUDRA loan chahiye (Hinglish)',
    '💼 I am an unemployed youth seeking skill training under PMKVY',
    '🏠 Mujhe PMAY ke tehat pucca ghar banane ke liye sahayata chahiye (Hinglish)',
    '👶 orphan child protection aur nutrition support ki jankari (Hinglish)',
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Handle passed query from Landing Page
  useEffect(() => {
    const initialQuery = (location.state as any)?.initialQuery;
    if (initialQuery) {
      handleSendMessage(initialQuery);
    }
  }, [location.state]);

  const handleSendMessage = async (messageText: string) => {
    if (!messageText.trim() || isTyping) return;

    const userTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: messageText.trim(),
      time: userTime,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const res = await sendAssistantChat(messageText);
      const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      if (res) {
        const botMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          text: cleanText(res.reply),
          time: botTime,
          matchedSchemes: res.matched_schemes,
          missingFields: res.missing_fields,
        };
        setMessages((prev) => [...prev, botMsg]);
      } else {
        const fallbackMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          text: '⚠️ Unable to connect to backend AI server. Please verify FastAPI backend service is running on http://localhost:8000.',
          time: botTime,
          isError: true,
        };
        setMessages((prev) => [...prev, fallbackMsg]);
        setToast({
          id: Date.now().toString(),
          type: 'error',
          title: 'Network Error',
          message: 'Failed to communicate with JanSathi AI service.',
        });
      }
    } catch (err) {
      console.error('Chat error:', err);
    } finally {
      setIsTyping(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleCreateReminderForScheme = async (scheme: MatchedScheme) => {
    try {
      const reminderData = {
        citizen_id: 1,
        scheme_id: scheme.id,
        title: `Deadline: ${scheme.title}`,
        category: scheme.category,
        reminder_date: scheme.deadline !== 'Open Year Round' ? scheme.deadline : '2026-11-30',
        status: 'pending',
      };

      await createReminder(reminderData);
      setReminderCreatedIds((prev) => [...prev, scheme.id]);

      setToast({
        id: Date.now().toString(),
        type: 'success',
        title: 'Reminder Created Successfully! 🔔',
        message: `Reminder set for "${scheme.title}" due on ${reminderData.reminder_date}. Check your Reminders page!`,
      });
    } catch (err) {
      setToast({
        id: Date.now().toString(),
        type: 'error',
        title: 'Reminder Failed',
        message: 'Could not create reminder. Please try again.',
      });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(inputMessage);
  };

  const handleResetChat = () => {
    setMessages([
      {
        id: Date.now().toString(),
        sender: 'assistant',
        text: 'Namaste! JanSathi AI chat conversation has been reset. How may I assist you today?',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
    setToast({
      id: Date.now().toString(),
      type: 'info',
      title: 'Chat Reset',
      message: 'Conversation history cleared.',
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      {/* Toast Notification Container */}
      <Toast toast={toast} onClose={() => setToast(null)} />

      {/* Header Banner */}
      <div className="flex items-center justify-between bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gov-saffron-500 to-gov-saffron-700 text-white flex items-center justify-center shadow">
            <Landmark className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-base sm:text-lg font-bold text-slate-900 flex items-center gap-2">
              JanSathi AI Case Worker
              <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full font-semibold border border-emerald-200">
                10 CITIZEN GROUPS
              </span>
            </h1>
            <p className="text-xs text-slate-500">Categorized Public Service Matching • Sarvam AI Grounded</p>
          </div>
        </div>

        <button
          onClick={handleResetChat}
          className="p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors focus:ring-2 focus:ring-amber-500 focus:outline-none"
          title="Reset Conversation"
          aria-label="Reset Conversation"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Main Interactive Chat Window */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[620px] overflow-hidden">
        
        {/* Messages Scroll Area */}
        <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-6 bg-[#f8fafc]">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start space-x-3 ${
                msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              {/* Sender Avatar */}
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center text-white shrink-0 shadow-sm ${
                  msg.sender === 'user'
                    ? 'bg-gov-navy-800'
                    : msg.isError
                    ? 'bg-rose-600'
                    : 'bg-gradient-to-br from-gov-saffron-500 to-gov-saffron-700'
                }`}
              >
                {msg.sender === 'user' ? (
                  <User className="w-4 h-4" />
                ) : msg.isError ? (
                  <AlertCircle className="w-4 h-4" />
                ) : (
                  <Bot className="w-4 h-4" />
                )}
              </div>

              {/* Message Content Container */}
              <div className="max-w-[90%] sm:max-w-[82%] space-y-3">
                <div
                  className={`rounded-2xl p-4 text-xs sm:text-sm shadow-xs ${
                    msg.sender === 'user'
                      ? 'bg-gov-navy-800 text-white rounded-tr-none'
                      : msg.isError
                      ? 'bg-rose-50 border border-rose-200 text-rose-800 rounded-tl-none'
                      : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none leading-relaxed'
                  }`}
                >
                  <div className="whitespace-pre-line font-sans">{cleanText(msg.text)}</div>
                  
                  {/* Timestamp */}
                  <span
                    className={`text-[10px] block mt-2 text-right font-medium ${
                      msg.sender === 'user' ? 'text-slate-300' : 'text-slate-400'
                    }`}
                  >
                    {msg.time}
                  </span>
                </div>

                {/* Missing Fields Callout */}
                {msg.missingFields && msg.missingFields.length > 0 && (
                  <div className="bg-amber-50 border border-amber-200 p-3 rounded-xl flex items-start space-x-2 text-xs text-amber-900">
                    <HelpCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold">Follow-up Info Needed:</span> Providing your{' '}
                      <span className="font-semibold">{msg.missingFields.join(', ')}</span> will help narrow down exact eligible schemes!
                    </div>
                  </div>
                )}

                {/* AI Scheme Cards */}
                {msg.matchedSchemes && msg.matchedSchemes.length > 0 && (
                  <div className="space-y-3 pt-2">
                    <div className="flex items-center space-x-1.5 text-xs font-bold text-gov-navy-900">
                      <Sparkles className="w-4 h-4 text-gov-saffron-500 animate-pulse" />
                      <span>Matched Government Schemes ({msg.matchedSchemes.length})</span>
                    </div>

                    <div className="grid grid-cols-1 gap-3">
                      {msg.matchedSchemes.map((scheme) => {
                        const isReminderSet = reminderCreatedIds.includes(scheme.id);
                        return (
                          <div
                            key={scheme.id}
                            className="bg-white border border-slate-200 hover:border-gov-saffron-400 rounded-xl p-4 shadow-sm transition-all space-y-3"
                          >
                            {/* Card Top Row */}
                            <div className="flex items-start justify-between gap-2">
                              <div>
                                <span className="inline-block text-[10px] font-bold text-gov-saffron-700 bg-gov-saffron-50 px-2.5 py-0.5 rounded-full border border-gov-saffron-200 mb-1">
                                  {scheme.category}
                                </span>
                                <h4 className="text-sm font-bold text-slate-900">{scheme.title}</h4>
                              </div>
                              <span className="inline-flex items-center space-x-1 text-[10px] text-slate-600 bg-slate-100 px-2 py-1 rounded-md shrink-0 font-medium border border-slate-200">
                                <Calendar className="w-3 h-3 text-slate-500" />
                                <span>{scheme.deadline}</span>
                              </span>
                            </div>

                            {/* Description */}
                            <p className="text-xs text-slate-600 leading-relaxed">{scheme.description}</p>

                            {/* Match Reason & Required Documents */}
                            <div className="bg-slate-50 p-3 rounded-lg space-y-2 text-xs border border-slate-100">
                              <div className="flex items-start space-x-2 text-slate-700">
                                <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                                <div>
                                  <span className="font-semibold text-slate-900">Why You Are Eligible:</span>{' '}
                                  <span className="text-slate-600">{cleanText(scheme.match_reason || scheme.eligibility)}</span>
                                </div>
                              </div>

                              <div className="flex items-start space-x-2 text-slate-700 pt-1 border-t border-slate-200/60">
                                <FileText className="w-4 h-4 text-gov-navy-600 shrink-0 mt-0.5" />
                                <div>
                                  <span className="font-semibold text-slate-900">Required Documents:</span>{' '}
                                  <span className="text-slate-600">{scheme.required_documents}</span>
                                </div>
                              </div>
                            </div>

                            {/* Card Footer Actions */}
                            <div className="flex items-center justify-between pt-1 border-t border-slate-100 flex-wrap gap-2">
                              <span className="text-[10px] text-slate-400 font-medium">Scheme ID #{scheme.id}</span>

                              <div className="flex items-center space-x-2">
                                {scheme.official_link && scheme.official_link.startsWith('http') && (
                                  <a
                                    href={scheme.official_link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 transition-colors"
                                  >
                                    <ExternalLink className="w-3.5 h-3.5 text-gov-navy-600" />
                                    <span>Official myScheme Link</span>
                                  </a>
                                )}

                                <button
                                  onClick={() => handleCreateReminderForScheme(scheme)}
                                  disabled={isReminderSet}
                                  className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all focus:ring-2 focus:ring-amber-500 focus:outline-none ${
                                    isReminderSet
                                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 cursor-default'
                                      : 'bg-gov-saffron-600 hover:bg-gov-saffron-700 text-white shadow'
                                  }`}
                                >
                                  {isReminderSet ? (
                                    <>
                                      <Check className="w-3.5 h-3.5" />
                                      <span>Reminder Set</span>
                                    </>
                                  ) : (
                                    <>
                                      <BellPlus className="w-3.5 h-3.5" />
                                      <span>Set Reminder</span>
                                    </>
                                  )}
                                </button>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex items-center space-x-3 animate-in fade-in duration-200">
              <div className="w-9 h-9 rounded-full bg-gov-saffron-600 text-white flex items-center justify-center shrink-0 shadow-sm">
                <Bot className="w-4 h-4 animate-bounce" />
              </div>
              <div className="bg-white border border-slate-200 px-4 py-3 rounded-2xl rounded-tl-none text-xs text-slate-600 flex items-center space-x-2 shadow-xs">
                <div className="flex items-center space-x-1">
                  <span className="w-2 h-2 rounded-full bg-gov-saffron-500 animate-ping" />
                  <span className="w-1.5 h-1.5 rounded-full bg-gov-saffron-600" />
                  <span className="w-1.5 h-1.5 rounded-full bg-gov-saffron-700" />
                </div>
                <span className="font-medium text-slate-500">JanSathi AI case worker is evaluating 30+ government schemes...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* 15 Demo Suggestion Pills */}
        <div className="px-4 py-2 bg-white border-t border-slate-100">
          <div className="flex items-center space-x-1.5 text-[11px] font-medium text-slate-500 mb-1.5">
            <Sparkles className="w-3.5 h-3.5 text-gov-saffron-500" />
            <span>15 Demo Conversations (Select Any Citizen Group):</span>
          </div>
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
            {sampleQueries.map((query, idx) => (
              <button
                key={idx}
                disabled={isTyping}
                onClick={() => handleSendMessage(query)}
                className="whitespace-nowrap text-[11px] px-3 py-1.5 rounded-full bg-gov-ash hover:bg-gov-saffron-50 text-slate-700 hover:text-gov-saffron-700 border border-slate-200 transition-colors focus:ring-2 focus:ring-amber-500 focus:outline-none disabled:opacity-50"
              >
                {query}
              </button>
            ))}
          </div>
        </div>

        {/* Bottom Input Form */}
        <form onSubmit={handleSubmit} className="p-3 bg-white border-t border-slate-200 flex items-center space-x-2">
          <input
            ref={inputRef}
            type="text"
            disabled={isTyping}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your details (e.g. 'I am a 60 year old farmer from UP needing pension')..."
            className="flex-1 px-4 py-3 text-xs sm:text-sm bg-gov-ash border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gov-saffron-500 text-slate-800 placeholder-slate-400 disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isTyping}
            className="px-4 py-3 bg-gov-saffron-600 hover:bg-gov-saffron-700 disabled:opacity-50 text-white rounded-xl font-semibold shadow flex items-center space-x-1 transition-colors focus:ring-2 focus:ring-amber-500 focus:outline-none shrink-0 text-xs sm:text-sm"
          >
            <span>{isTyping ? 'Processing...' : 'Send'}</span>
            <Send className="w-4 h-4 ml-1" />
          </button>
        </form>
      </div>
    </div>
  );
};
