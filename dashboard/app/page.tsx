'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Header from '@/components/Header';
import StatsCards from '@/components/StatsCards';
import QuizForm from '@/components/QuizForm';
import HistoryList from '@/components/HistoryList';
import LiveLogs from '@/components/LiveLogs';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

interface QuizHistory {
  timestamp: string;
  email: string;
  initial_url: string;
  final_url?: string;
  status: string;
  time_taken: number;
  quiz_count?: number;
  error?: string;
}

interface ServiceStatus {
  service: string;
  status: string;
  version: string;
}

export default function Home() {
  const [history, setHistory] = useState<QuizHistory[]>([]);
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  // Fetch service status
  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/`);
      setServiceStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch status:', error);
    }
  };

  // Fetch quiz history
  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/history`);
      setHistory(response.data.history || []);
    } catch (error) {
      console.error('Failed to fetch history:', error);
      addLog('Error fetching history');
    }
  };

  // Submit quiz
  const submitQuiz = async (email: string, secret: string, url: string) => {
    setLoading(true);
    addLog(`Submitting quiz: ${url}`);

    try {
      const response = await axios.post(`${BACKEND_URL}/quiz`, {
        email,
        secret,
        url,
      });

      addLog(`Quiz completed: ${response.data.status}`);
      addLog(`Time taken: ${response.data.time_taken.toFixed(2)}s`);
      addLog(`Final answer: ${JSON.stringify(response.data.final_answer)}`);
      
      // Refresh history
      await fetchHistory();
      
      return response.data;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message;
      addLog(`Error: ${errorMsg}`);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Add log entry
  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev].slice(0, 100));
  };

  // Initial load
  useEffect(() => {
    fetchStatus();
    fetchHistory();
    
    // Refresh history every 30 seconds
    const interval = setInterval(fetchHistory, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Calculate stats
  const stats = {
    total: history.length,
    success: history.filter(h => h.status === 'success').length,
    failed: history.filter(h => h.status === 'failed').length,
    avgTime: history.length > 0
      ? history.reduce((sum, h) => sum + h.time_taken, 0) / history.length
      : 0,
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header serviceStatus={serviceStatus} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <StatsCards stats={stats} />

        {/* Main content */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left column - Quiz form and logs */}
          <div className="space-y-8">
            <QuizForm onSubmit={submitQuiz} loading={loading} />
            <LiveLogs logs={logs} />
          </div>

          {/* Right column - History */}
          <div>
            <HistoryList history={history} onRefresh={fetchHistory} />
          </div>
        </div>
      </main>
    </div>
  );
}
