import React from 'react';
import { Loader2, CheckCircle } from 'lucide-react';

interface ExecutionLogProps {
  crawlingStatus: string;
  crawlLogs: string[];
}

export function ExecutionLog({ crawlingStatus, crawlLogs }: ExecutionLogProps) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-black tracking-tight flex items-center gap-3">
          <Loader2 className={`${crawlingStatus === 'running' ? 'animate-spin' : ''}`} />
          CRAWL TERMINAL
        </h2>
        <p className="text-gray-600 font-medium mt-2">Real-time scanner log feed.</p>
      </div>

      <div className="bg-pink-50 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-md p-6 flex justify-between items-center">
        <div>
          <div className="text-xs font-black text-gray-600 uppercase tracking-widest">Job Status</div>
          <div className="text-xl font-black uppercase mt-1 flex items-center gap-2">
            {crawlingStatus === 'running' && <span className="h-3 w-3 rounded-none bg-black animate-pulse border border-black"></span>}
            {crawlingStatus === 'completed' && <CheckCircle className="h-5 w-5 text-black" />}
            {crawlingStatus}
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs font-black text-gray-600 uppercase tracking-widest">Routing</div>
          <div className="text-sm font-bold mt-1">Consolidating paths...</div>
        </div>
      </div>

      {/* Console box */}
      <div className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-md p-6 font-mono text-sm space-y-3 h-96 overflow-y-auto">
        {crawlLogs.map((log, i) => (
          <div key={i} className="text-black border-b border-gray-100 pb-2">
            <span className="text-gray-400 font-bold mr-3">{new Date().toLocaleTimeString()}</span>
            {log}
          </div>
        ))}
        {crawlingStatus === 'running' && (
          <div className="text-pink-600 font-bold flex items-center gap-2 animate-pulse mt-4">
            <Loader2 className="h-4 w-4 animate-spin" />
            &gt; Scanner engaged. Analyzing interactive DOM nodes...
          </div>
        )}
        {crawlLogs.length === 0 && (
          <div className="text-gray-400 font-bold text-center py-32 uppercase tracking-widest">
            No logs available. Initialize Analysis.
          </div>
        )}
      </div>
    </div>
  );
}
