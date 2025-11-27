'use client';

interface LiveLogsProps {
  logs: string[];
}

export default function LiveLogs({ logs }: LiveLogsProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Live Logs
          </h2>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-500 dark:text-gray-400">Live</span>
          </div>
        </div>
      </div>

      <div className="bg-gray-900 text-gray-100 p-4 font-mono text-xs max-h-[400px] overflow-y-auto">
        {logs.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            Waiting for logs...
          </div>
        ) : (
          <div className="space-y-1">
            {logs.map((log, index) => (
              <div key={index} className="hover:bg-gray-800 px-2 py-1 rounded">
                {log}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
