'use client';

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

interface HistoryListProps {
  history: QuizHistory[];
  onRefresh: () => void;
}

export default function HistoryList({ history, onRefresh }: HistoryListProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Quiz History
          </h2>
          <button
            onClick={onRefresh}
            className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            aria-label="Refresh history"
          >
            <svg className="w-5 h-5 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      <div className="max-h-[600px] overflow-y-auto">
        {history.length === 0 ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            <svg className="mx-auto h-12 w-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>No quiz history yet</p>
            <p className="text-sm mt-1">Submit a quiz to see results here</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {history.map((item, index) => (
              <div key={index} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      {item.status === 'success' ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400">
                          ✓ Success
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400">
                          ✗ Failed
                        </span>
                      )}
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(item.timestamp).toLocaleString()}
                      </span>
                    </div>

                    <p className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                      {item.email}
                    </p>

                    <p className="text-xs text-gray-600 dark:text-gray-400 truncate mb-1">
                      {item.initial_url}
                    </p>

                    <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {item.time_taken.toFixed(2)}s
                      </span>
                      {item.quiz_count && (
                        <span className="flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                          </svg>
                          {item.quiz_count} quiz{item.quiz_count > 1 ? 'zes' : ''}
                        </span>
                      )}
                    </div>

                    {item.error && (
                      <p className="mt-2 text-xs text-red-600 dark:text-red-400">
                        {item.error}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
