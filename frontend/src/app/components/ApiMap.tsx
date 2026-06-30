import React from 'react';
import { Database } from 'lucide-react';

interface ApiRoute {
  id: string;
  method: string;
  url: string;
  request_body: any;
  mapped_action: string;
}

interface ApiMapProps {
  apis: ApiRoute[];
}

export function ApiMap({ apis }: ApiMapProps) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="display-title text-2xl flex items-center gap-3 text-[var(--ink)]">
          <Database className="h-7 w-7 text-[var(--pie-green-deep)]" />
          <span>Discovered API Maps</span>
        </h2>
        <p className="text-[var(--ink-soft)] text-xs font-semibold mt-1">Browser intent to direct background API request translations.</p>
      </div>

      <div className="space-y-6">
        {apis.map((api) => (
          <div key={api.id} className="bg-[var(--paper)] border border-[var(--line)] rounded-[24px] p-6 flex flex-col md:flex-row justify-between gap-6 shadow-sm hover:border-[var(--pie-green)] transition duration-200">
            <div>
              <div className="flex items-center gap-4 mb-4">
                <span className="bg-[var(--ink)] text-[var(--cream)] font-bold px-3.5 py-1 text-xs uppercase tracking-wider rounded-full">
                  {api.method}
                </span>
                <code className="text-sm font-bold font-mono text-[var(--ink)]">{api.url}</code>
              </div>
              <div className="text-xs font-semibold text-[var(--ink-soft)] bg-[var(--cream)] border border-[var(--line)] px-4 py-2.5 rounded-full inline-block">
                Resolved Action: <strong className="text-[var(--ink)] uppercase font-extrabold">{api.mapped_action}</strong>
              </div>
            </div>

            <div className="md:w-1/2">
              <div className="text-[10px] font-bold text-[var(--ink-soft)] uppercase tracking-wider mb-2">Expected Payload Schema</div>
              <pre className="bg-[var(--code-bg)] text-[var(--code-text)] p-4 rounded-[16px] border border-[var(--line)] font-mono text-xs overflow-x-auto shadow-inner">
                {JSON.stringify(api.request_body, null, 2)}
              </pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
