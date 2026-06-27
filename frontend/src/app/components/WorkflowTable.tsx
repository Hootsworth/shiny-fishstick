import React from 'react';
import { Compass } from 'lucide-react';

interface Parameter {
  name: string;
  type: string;
  selector?: string;
}

interface Action {
  id: string;
  name: string;
  description: string;
  action_type: string;
  confidence_score: number;
  selector: string;
  parameters: string;
}

interface WorkflowTableProps {
  actions: Action[];
}

export function WorkflowTable({ actions }: WorkflowTableProps) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-black tracking-tight flex items-center gap-3">
          <Compass className="h-8 w-8" />
          ACTION DICTIONARY
        </h2>
        <p className="text-gray-600 font-medium mt-2">Classified DOM elements and agent intents.</p>
      </div>

      <div className="space-y-6">
        {actions.map((act) => {
          let params: Parameter[] = [];
          try {
            params = JSON.parse(act.parameters || "[]");
          } catch (e) {
            console.error("Failed to parse action parameters", e);
          }

          return (
            <div key={act.id} className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-md p-6 transition-transform hover:-translate-y-1 hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
              <div className="flex flex-col md:flex-row justify-between md:items-center gap-4 border-b-2 border-gray-100 pb-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="text-xl font-black uppercase">{act.name}</h3>
                    <span className={`px-3 py-1 border-2 border-black font-bold text-xs uppercase tracking-wider ${act.action_type === 'api' ? 'bg-pink-200' : 'bg-gray-100'}`}>
                      {act.action_type}
                    </span>
                  </div>
                  <p className="text-gray-600 font-medium mt-2">{act.description}</p>
                </div>
                <div className="text-right">
                  <span className="block text-xs font-bold text-gray-500 uppercase tracking-widest">Confidence</span>
                  <strong className="text-2xl font-black">{(act.confidence_score * 100).toFixed(0)}%</strong>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="text-xs font-black text-gray-500 mb-2 uppercase tracking-widest">Anchor Selector</div>
                  <code className="block bg-gray-50 p-2 border-2 border-black rounded-none font-mono text-sm font-bold">{act.selector}</code>
                </div>
                <div>
                  <div className="text-xs font-black text-gray-500 mb-2 uppercase tracking-widest">Required Params</div>
                  {params.length > 0 ? (
                    <div className="space-y-2">
                      {params.map((p, idx) => (
                        <div key={idx} className="text-sm font-medium flex items-center gap-2 bg-gray-50 p-2 border-2 border-black">
                          <strong className="text-black">{p.name}</strong>
                          <span className="text-gray-500 text-xs uppercase">({p.type})</span>
                          {p.selector && <code className="ml-auto text-xs bg-white px-2 py-1 border border-black font-mono">{p.selector}</code>}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <span className="block bg-gray-50 p-2 border-2 border-black font-medium text-sm text-gray-500 italic">No parameters required</span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
