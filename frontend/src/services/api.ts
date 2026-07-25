import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

export interface HealthResponse {
  status: string;
}

export interface Citizen {
  id: number;
  name: string;
  phone: string;
  language?: string;
  district?: string;
  state?: string;
  created_at?: string;
}

export interface Scheme {
  id: number;
  title: string;
  category: string;
  description: string;
  eligibility: string;
  required_documents: string;
  deadline?: string;
}

export interface MatchedScheme {
  id: number;
  title: string;
  category: string;
  description: string;
  eligibility: string;
  required_documents: string;
  deadline: string;
  match_reason: string;
}

export interface AssistantChatResponse {
  reply: string;
  matched_schemes: MatchedScheme[];
  missing_fields: string[];
  can_create_reminder: boolean;
}

export interface Reminder {
  id: number;
  citizen_id: number;
  scheme_id?: number;
  title: string;
  category?: string;
  reminder_date: string;
  status: string;
  created_at?: string;
  scheme?: Scheme;
}

export const checkHealth = async (): Promise<HealthResponse> => {
  try {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return { status: 'error' };
  }
};

export const getSchemes = async (category?: string): Promise<Scheme[]> => {
  try {
    const response = await api.get<Scheme[]>('/api/schemes', {
      params: { category },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching schemes:', error);
    return [];
  }
};

export const getReminders = async (citizenId?: number, status?: string): Promise<Reminder[]> => {
  try {
    const response = await api.get<Reminder[]>('/api/reminders', {
      params: { citizen_id: citizenId, status },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching reminders:', error);
    return [];
  }
};

export const createReminder = async (data: Partial<Reminder>): Promise<Reminder | null> => {
  try {
    const response = await api.post<Reminder>('/api/reminders', data);
    return response.data;
  } catch (error) {
    console.error('Error creating reminder:', error);
    return null;
  }
};

export const updateReminderStatus = async (id: number, status: string): Promise<Reminder | null> => {
  try {
    const response = await api.patch<Reminder>(`/api/reminders/${id}`, { status });
    return response.data;
  } catch (error) {
    console.error('Error updating reminder status:', error);
    return null;
  }
};

export const sendAssistantChat = async (message: string): Promise<AssistantChatResponse | null> => {
  try {
    const response = await api.post<AssistantChatResponse>('/api/assistant/chat', {
      message,
    });
    return response.data;
  } catch (error) {
    console.error('Assistant chat request failed:', error);
    return null;
  }
};
