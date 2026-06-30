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
        <h2 className="display-title text-2xl flex items-center gap-3 text-[var(--ink)]">
          <Loader2 className={`h-7 w-7 text-[var(--pie-green-deep)] ${crawlingStatus === 'running' ? 'animate-spin' : ''}`} />
          <span>Scanner Logs</span>
        </h2>
        <p className="text-[var(--ink-soft)] text-xs font-semibold mt-1">Real-time scan logs and process terminal outputs feed.</p>
      </div>

      {/* Status summary banner */}
      <div className="bg-[var(--paper)] border border-[var(--line)] rounded-[24px] p-6 flex justify-between items-center shadow-sm">
        <div>
          <div className="text-[10px] font-bold text-[var(--ink-soft)] uppercase tracking-wider">Job Status</div>
          <div className="text-lg font-extrabold uppercase mt-1 flex items-center gap-2 text-[var(--ink)] tracking-tight">
            {crawlingStatus === 'running' && <span className="h-2.5 w-2.5 rounded-full bg-[var(--pie-green)] animate-pulse"></span>}
            {crawlingStatus === 'completed' && <CheckCircle className="h-5 w-5 text-[var(--pie-green-deep)]" />}
            <span>{crawlingStatus}</span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-[10px] font-bold text-[var(--ink-soft)] uppercase tracking-wider font-sans">Pipeline State</div>
          <div className="text-xs font-semibold mt-1 text-[var(--ink)]">Consolidating routes...</div>
        </div>
      </div>

      {/* Terminal log panel */}
      <div className="bg-[var(--code-bg)] text-[var(--code-text)] border border-[var(--line)] rounded-[24px] p-6 font-mono text-xs space-y-3 h-96 overflow-y-auto shadow-sm">
        {crawlLogs.map((log, i) => (
          <div key={i} className="border-b border-[var(--ink)] border-opacity-10 pb-2">
            <span className="text-[var(--ink-soft)] font-bold mr-3">{new Date().toLocaleTimeString()}</span>
            <span>{log}</span>
          </div>
        ))}
        {crawlingStatus === 'running' && (
          <div className="text-[var(--pie-green)] font-bold flex items-center gap-2 animate-pulse mt-4">
            <Loader2 className="h-4.5 w-4.5 animate-spin" />
            <span>&gt; Scanner engaged. Identifying active interactive DOM layers...</span>
          </div>
        )}
        {crawlLogs.length === 0 && (
          <div className="text-[var(--ink-soft)] font-bold text-center py-32 uppercase tracking-widest opacity-60">
            Terminal inactive. Trigger crawl compilation to view logs.
          </div>
        )}
      </div>
    </div>
  );
}
