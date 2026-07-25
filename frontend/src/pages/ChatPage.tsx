import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  Landmark, 
  RefreshCw, 
  BellPlus, 
  Check 
} from 'lucide-react';
import { sendAssistantChat, MatchedScheme, createReminder } from '../services/api';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  time: string;
  matchedSchemes?: MatchedScheme[];
  missingFields?: string[];
}

export const ChatPage: React.FC = () => {
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [reminderCreatedIds, setReminderCreatedIds] = useState<number[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'assistant',
      text: 'Namaste! I am your AI Case Worker. Tell me about your age, state, occupation, or what assistance you are seeking (Scholarships, Farming, Pensions, Women Welfare, or Health Insurance).',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sampleQueries = [
    'I am a 65 year old farmer needing pension and crop assistance',
    'I am a female student in Class 9 seeking scholarship guidance',
    'Tell me about Ayushman Bharat health cover for my family',
    'What schemes are available for Lakhpati Didi & women SHGs?',
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (messageText: string) => {
    if (!messageText.trim()) return;

    const userTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: messageText,
      time: userTime,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsTyping(true);

    // Call Backend AI Case Worker endpoint
    const res = await sendAssistantChat(messageText);

    const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    setIsTyping(false);

    if (res) {
      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: res.reply,
        time: botTime,
        matchedSchemes: res.matched_schemes,
        missingFields: res.missing_fields,
      };
      setMessages((prev) => [...prev, botMsg]);
    } else {
      // Fallback response if offline
      const fallbackMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: 'I have logged your request. (Note: Connecting to local backend API. Make sure FastAPI server is running).',
        time: botTime,
      };
      setMessages((prev) => [...prev, fallbackMsg]);
    }
  };

  const handleCreateReminderForScheme = async (scheme: MatchedScheme) => {
    const reminderData = {
      citizen_id: 1,
      scheme_id: scheme.id,
      title: `Application Deadline: ${scheme.title}`,
      category: scheme.category,
      reminder_date: scheme.deadline !== 'Open Year Round' ? scheme.deadline : '2026-11-30',
      status: 'pending',
    };

    await createReminder(reminderData);
    setReminderCreatedIds((prev) => [...prev, scheme.id]);
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
        text: 'Chat conversation reset. Ask me any question regarding public services or government schemes!',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      {/* Header Banner */}
      <div className="flex items-center justify-between bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gov-saffron-500 to-gov-saffron-700 text-white flex items-center justify-center shadow">
            <Landmark className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              JanSathi AI Case Worker
              <span className="text-[10px] bg-gov-saffron-100 text-gov-saffron-700 px-2 py-0.5 rounded font-semibold border border-gov-saffron-200">
                LIVE API
              </span>
            </h1>
            <p className="text-xs text-slate-500">Public Service Matching • Modular AI Assistant</p>
          </div>
        </div>

        <button
          onClick={handleResetChat}
          className="p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
          title="Reset Conversation"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Main Interactive Chat Area */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[600px] overflow-hidden">
        {/* Messages Feed */}
        <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-5 bg-[#f8fafc]">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start space-x-3 ${
                msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center text-white shrink-0 shadow-sm ${
                  msg.sender === 'user'
                    ? 'bg-gov-navy-800'
                    : 'bg-gradient-to-br from-gov-saffron-500 to-gov-saffron-700'
                }`}
              >
                {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Chat Bubble & Scheme Cards */}
              <div className="max-w-[90%] sm:max-w-[80%] space-y-3">
                <div
                  className={`rounded-2xl p-4 text-xs sm:text-sm shadow-xs ${
                    msg.sender === 'user'
                      ? 'bg-gov-navy-800 text-white rounded-tr-none'
                      : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none leading-relaxed'
                  }`}
                >
                  <div className="whitespace-pre-line font-sans">{msg.text}</div>
                  <span
                    className={`text-[10px] block mt-2 text-right ${
                      msg.sender === 'user' ? 'text-slate-300' : 'text-slate-400'
                    }`}
                  >
                    {msg.time}
                  </span>
                </div>

                {/* Inline Matched Scheme Cards */}
                {msg.matchedSchemes && msg.matchedSchemes.length > 0 && (
                  <div className="space-y-3 pt-1">
                    <div className="flex items-center space-x-1.5 text-xs font-bold text-gov-navy-900">
                      <Sparkles className="w-4 h-4 text-gov-saffron-500" />
                      <span>Recommended Schemes ({msg.matchedSchemes.length})</span>
                    </div>

                    <div className="grid grid-cols-1 gap-3">
                      {msg.matchedSchemes.map((scheme) => {
                        const isReminderSet = reminderCreatedIds.includes(scheme.id);
                        return (
                          <div
                            key={scheme.id}
                            className="bg-white border border-slate-200/90 hover:border-gov-saffron-400 rounded-xl p-4 shadow-sm transition-all space-y-3"
                          >
                            <div className="flex items-start justify-between gap-2">
                              <div>
                                <span className="inline-block text-[10px] font-bold text-gov-saffron-700 bg-gov-saffron-50 px-2 py-0.5 rounded border border-gov-saffron-200 mb-1">
                                  {scheme.category}
                                </span>
                                <h4 className="text-sm font-bold text-slate-900">{scheme.title}</h4>
                              </div>
                              <span className="text-[10px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded shrink-0 font-medium">
                                Deadline: {scheme.deadline}
                              </span>
                            </div>

                            <p className="text-xs text-slate-600 leading-relaxed">{scheme.description}</p>

                            <div className="bg-gov-ash/70 p-2.5 rounded-lg space-y-1.5 text-xs text-slate-700 border border-slate-100">
                              <div>
                                <span className="font-semibold text-gov-navy-800">Match Reason:</span>{' '}
                                <span className="text-slate-600">{scheme.match_reason}</span>
                              </div>
                              <div>
                                <span className="font-semibold text-gov-navy-800">Required Documents:</span>{' '}
                                <span className="text-slate-600">{scheme.required_documents}</span>
                              </div>
                            </div>

                            <div className="flex items-center justify-between pt-1 border-t border-slate-100">
                              <span className="text-[10px] text-slate-400 font-medium">JanSathi Scheme #0{scheme.id}</span>

                              <button
                                onClick={() => handleCreateReminderForScheme(scheme)}
                                disabled={isReminderSet}
                                className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                                  isReminderSet
                                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                    : 'bg-gov-saffron-600 hover:bg-gov-saffron-700 text-white shadow focus-ring'
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
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-full bg-gov-saffron-600 text-white flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 animate-bounce" />
              </div>
              <div className="bg-white border border-slate-200 px-4 py-3 rounded-2xl rounded-tl-none text-xs text-slate-500 flex items-center space-x-2 shadow-xs">
                <span className="w-2 h-2 rounded-full bg-gov-saffron-500 animate-ping" />
                <span>AI Case Worker is searching scheme database...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestion Pills */}
        <div className="px-4 py-2 bg-white border-t border-slate-100">
          <div className="flex items-center space-x-1.5 text-[11px] font-medium text-slate-500 mb-2">
            <Sparkles className="w-3.5 h-3.5 text-gov-saffron-500" />
            <span>Try AI Case Worker prompts:</span>
          </div>
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
            {sampleQueries.map((query, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(query)}
                className="whitespace-nowrap text-[11px] px-3 py-1.5 rounded-full bg-gov-ash hover:bg-gov-saffron-50 text-slate-700 hover:text-gov-saffron-700 border border-slate-200 transition-colors"
              >
                {query}
              </button>
            ))}
          </div>
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSubmit} className="p-3 bg-white border-t border-slate-200 flex items-center space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type details (e.g. 'I am a 65 year old farmer from UP looking for pension')..."
            className="flex-1 px-4 py-3 text-xs sm:text-sm bg-gov-ash border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gov-saffron-500 text-slate-800 placeholder-slate-400"
          />
          <button
            type="submit"
            disabled={!inputMessage.trim()}
            className="px-4 py-3 bg-gov-saffron-600 hover:bg-gov-saffron-700 disabled:opacity-50 text-white rounded-xl font-semibold shadow flex items-center space-x-1 transition-colors focus-ring shrink-0 text-xs sm:text-sm"
          >
            <span>Send</span>
            <Send className="w-4 h-4 ml-1" />
          </button>
        </form>
      </div>
    </div>
  );
};
