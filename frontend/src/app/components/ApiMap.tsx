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
        <h2 className="text-3xl font-black tracking-tight flex items-center gap-3">
          <Database className="h-8 w-8" />
          API MAPPER
        </h2>
        <p className="text-gray-600 font-medium mt-2">Browser intent to direct background API translations.</p>
      </div>

      <div className="space-y-6">
        {apis.map((api) => (
          <div key={api.id} className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-md p-6 flex flex-col md:flex-row justify-between gap-6">
            <div>
              <div className="flex items-center gap-4 mb-4">
                <span className="bg-black text-white font-black px-3 py-1.5 text-sm uppercase tracking-wider shadow-[2px_2px_0px_0px_#f472b6] border border-black">
                  {api.method}
                </span>
                <code className="text-lg font-bold font-mono">{api.url}</code>
              </div>
              <div className="text-sm font-medium text-gray-600 bg-pink-50 border border-black p-3 inline-block">
                Resolved Intent: <strong className="text-black uppercase">{api.mapped_action}</strong>
              </div>
            </div>

            <div className="md:w-1/2">
              <div className="text-xs font-black text-gray-500 uppercase tracking-widest mb-2">Expected Payload</div>
              <pre className="bg-gray-50 p-4 border-2 border-black font-mono text-sm font-bold text-black overflow-x-auto">
                {JSON.stringify(api.request_body, null, 2)}
              </pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
