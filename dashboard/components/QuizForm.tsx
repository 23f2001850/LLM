'use client';

import { useState } from 'react';

interface QuizFormProps {
  onSubmit: (email: string, secret: string, url: string) => Promise<any>;
  loading: boolean;
}

export default function QuizForm({ onSubmit, loading }: QuizFormProps) {
  const [email, setEmail] = useState('');
  const [secret, setSecret] = useState('');
  const [url, setUrl] = useState('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResult(null);

    try {
      const data = await onSubmit(email, secret, url);
      setResult(data);
      
      // Clear form on success
      if (data.status === 'ok') {
        setEmail('');
        setSecret('');
        setUrl('');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
        Submit Quiz
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-primary-500 focus:ring-primary-500 px-4 py-2"
            placeholder="student@example.com"
          />
        </div>

        <div>
          <label htmlFor="secret" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Secret Key
          </label>
          <input
            type="password"
            id="secret"
            value={secret}
            onChange={(e) => setSecret(e.target.value)}
            required
            className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-primary-500 focus:ring-primary-500 px-4 py-2"
            placeholder="Enter your secret key"
          />
        </div>

        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Quiz URL
          </label>
          <input
            type="url"
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
            className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-primary-500 focus:ring-primary-500 px-4 py-2"
            placeholder="https://example.com/quiz"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : (
            'Submit Quiz'
          )}
        </button>
      </form>

      {/* Error display */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-800 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Success display */}
      {result && result.status === 'ok' && (
        <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <h3 className="text-sm font-medium text-green-800 dark:text-green-400 mb-2">
            Quiz completed successfully!
          </h3>
          <div className="text-xs text-green-700 dark:text-green-300 space-y-1">
            <p>Time: {result.time_taken.toFixed(2)}s</p>
            <p>Answer: {JSON.stringify(result.final_answer)}</p>
            <p>Steps: {result.steps.length}</p>
          </div>
        </div>
      )}
    </div>
  );
}
