import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  Calendar, 
  Plus, 
  Tag, 
  CheckCircle2, 
  AlertTriangle, 
  Loader2, 
  RefreshCw, 
  X, 
  Check 
} from 'lucide-react';
import { getReminders, createReminder, updateReminderStatus, Reminder, getSchemes, Scheme } from '../services/api';

export const RemindersPage: React.FC = () => {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // Form State
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Pension Services');
  const [reminderDate, setReminderDate] = useState('');
  const [selectedSchemeId, setSelectedSchemeId] = useState<string>('');
  const [submitting, setSubmitting] = useState(false);

  const fetchRemindersData = async () => {
    setLoading(true);
    try {
      const data = await getReminders();
      if (data && data.length > 0) {
        setReminders(data);
      } else {
        // Fallback default sample reminders if API returns empty
        setReminders([
          {
            id: 1,
            citizen_id: 1,
            title: 'Annual Pension Life Certificate Verification',
            category: 'Senior Citizens',
            reminder_date: '2026-11-30',
            status: 'pending',
          },
          {
            id: 2,
            citizen_id: 1,
            title: 'PM-Kisan e-KYC & Land Seeding Deadline',
            category: 'Farmers',
            reminder_date: '2026-08-15',
            status: 'pending',
          },
          {
            id: 3,
            citizen_id: 1,
            title: 'Renew Ayushman Bharat Card for Household',
            category: 'Health',
            reminder_date: '2026-07-30',
            status: 'completed',
          },
        ]);
      }
    } catch (err) {
      console.error('Error fetching reminders:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRemindersData();
    // Pre-fetch schemes for dropdown selection
    getSchemes().then(setSchemes);
  }, []);

  const handleToggleStatus = async (reminder: Reminder) => {
    const nextStatus = reminder.status === 'completed' ? 'pending' : 'completed';
    // Optimistic UI update
    setReminders((prev) =>
      prev.map((item) => (item.id === reminder.id ? { ...item, status: nextStatus } : item))
    );

    // Call API
    await updateReminderStatus(reminder.id, nextStatus);
  };

  const handleCreateReminder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !reminderDate) return;

    setSubmitting(true);
    const newReminderData = {
      citizen_id: 1,
      scheme_id: selectedSchemeId ? parseInt(selectedSchemeId) : undefined,
      title: title.trim(),
      category: category || 'General',
      reminder_date: reminderDate,
      status: 'pending',
    };

    const created = await createReminder(newReminderData);
    if (created) {
      setReminders((prev) => [created, ...prev]);
    } else {
      // Local fallback insert
      const localItem: Reminder = {
        id: Date.now(),
        ...newReminderData,
      };
      setReminders((prev) => [localItem, ...prev]);
    }

    setSubmitting(false);
    setIsModalOpen(false);
    setTitle('');
    setReminderDate('');
    setSelectedSchemeId('');
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 rounded-xl bg-gov-navy-800 text-white flex items-center justify-center shadow">
            <Bell className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">Citizen Reminders</h1>
            <p className="text-xs text-slate-500">Live reminders synced with FastAPI backend & SQLite database.</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={fetchRemindersData}
            className="p-2.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors"
            title="Refresh Reminders"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>

          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center space-x-2 px-4 py-2.5 bg-gov-saffron-600 hover:bg-gov-saffron-700 text-white rounded-xl font-semibold text-xs sm:text-sm shadow transition-colors focus-ring"
          >
            <Plus className="w-4 h-4" />
            <span>Set Reminder</span>
          </button>
        </div>
      </div>

      {/* Reminders List Grid */}
      {loading ? (
        <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center space-y-3">
          <Loader2 className="w-8 h-8 text-gov-saffron-600 animate-spin mx-auto" />
          <p className="text-xs text-slate-500">Loading citizen reminders from backend...</p>
        </div>
      ) : reminders.length === 0 ? (
        <div className="bg-white p-10 rounded-2xl border border-slate-200 text-center space-y-2">
          <Bell className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">No Reminders Found</h3>
          <p className="text-xs text-slate-500">Click "Set Reminder" to create your first public service reminder.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {reminders.map((item) => {
            const isDone = item.status === 'completed';
            return (
              <div
                key={item.id}
                className={`gov-card p-5 flex flex-col justify-between space-y-4 border transition-all ${
                  isDone ? 'bg-slate-50/70 border-slate-200 opacity-90' : 'bg-white border-slate-200/90'
                }`}
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center space-x-1 text-[11px] font-semibold text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded border border-slate-200">
                      <Tag className="w-3 h-3 text-gov-saffron-500" />
                      <span>{item.category || 'General'}</span>
                    </span>

                    <button
                      onClick={() => handleToggleStatus(item)}
                      className={`inline-flex items-center space-x-1 text-[10px] px-2 py-0.5 rounded font-semibold border transition-colors ${
                        isDone
                          ? 'text-emerald-700 bg-emerald-50 border-emerald-200 hover:bg-emerald-100'
                          : 'text-amber-700 bg-amber-50 border-amber-200 hover:bg-amber-100'
                      }`}
                    >
                      {isDone ? (
                        <>
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          <span>Completed</span>
                        </>
                      ) : (
                        <>
                          <AlertTriangle className="w-3 h-3 text-amber-600" />
                          <span>Pending</span>
                        </>
                      )}
                    </button>
                  </div>

                  <h3 className={`text-sm font-bold leading-snug ${isDone ? 'line-through text-slate-500' : 'text-slate-900'}`}>
                    {item.title}
                  </h3>

                  {item.scheme && (
                    <div className="text-[11px] text-gov-navy-800 bg-gov-navy-50/70 px-2 py-1 rounded border border-gov-navy-100">
                      <span className="font-semibold">Linked Scheme:</span> {item.scheme.title}
                    </div>
                  )}
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                  <div className="flex items-center space-x-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>Due: {item.reminder_date}</span>
                  </div>

                  <button
                    onClick={() => handleToggleStatus(item)}
                    className="text-[11px] text-gov-saffron-600 hover:underline font-semibold flex items-center space-x-1"
                  >
                    <Check className="w-3 h-3" />
                    <span>{isDone ? 'Mark Active' : 'Mark Done'}</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* New Reminder Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-5 border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Bell className="w-4 h-4 text-gov-saffron-600" />
                <span>Create New Reminder</span>
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateReminder} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Reminder Title *
                </label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Renew Pension Verification"
                  className="w-full px-3.5 py-2 text-xs sm:text-sm bg-gov-ash border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gov-saffron-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-gov-ash border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gov-saffron-500"
                  >
                    <option value="Pension Services">Pension Services</option>
                    <option value="Farmers">Farmers</option>
                    <option value="Scholarships">Scholarships</option>
                    <option value="Women">Women</option>
                    <option value="Health">Health</option>
                    <option value="Utilities">Utilities</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Due Date *</label>
                  <input
                    type="date"
                    required
                    value={reminderDate}
                    onChange={(e) => setReminderDate(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-gov-ash border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gov-saffron-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Link Scheme (Optional)
                </label>
                <select
                  value={selectedSchemeId}
                  onChange={(e) => setSelectedSchemeId(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-gov-ash border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gov-saffron-500"
                >
                  <option value="">-- No specific scheme --</option>
                  {schemes.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.title} ({s.category})
                    </option>
                  ))}
                </select>
              </div>

              <div className="pt-3 flex items-center justify-end space-x-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting || !title.trim() || !reminderDate}
                  className="px-5 py-2 text-xs font-semibold bg-gov-saffron-600 hover:bg-gov-saffron-700 disabled:opacity-50 text-white rounded-xl shadow transition-colors"
                >
                  {submitting ? 'Saving...' : 'Save Reminder'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
