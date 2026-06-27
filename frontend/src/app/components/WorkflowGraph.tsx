import React from 'react';
import { ChevronRight, Workflow } from 'lucide-react';

interface Step {
  action: string;
  source_page: string;
  target_page: string;
}

interface WorkflowItem {
  id: string;
  name: string;
  description: string;
  steps: Step[];
}

interface WorkflowGraphProps {
  workflows: WorkflowItem[];
}

export function WorkflowGraph({ workflows }: WorkflowGraphProps) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-black tracking-tight flex items-center gap-3">
          <Workflow className="h-8 w-8" />
          STATE MACHINES
        </h2>
        <p className="text-gray-600 font-medium mt-2">Sequential step logic mapped for agents.</p>
      </div>

      {workflows.map((wf) => (
        <div key={wf.id} className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-md p-8">
          <h3 className="text-xl font-black uppercase mb-2">{wf.name}</h3>
          <p className="text-gray-600 font-medium mb-10">{wf.description}</p>

          <div className="flex flex-col md:flex-row items-center justify-between gap-4 relative">
            {wf.steps.map((step, index) => (
              <React.Fragment key={index}>
                <div className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_#f472b6] p-6 w-full md:w-64 text-center relative z-10">
                  <div className="text-xs font-black text-pink-500 uppercase tracking-widest bg-pink-50 inline-block px-2 py-1 border border-pink-200 mb-3">
                    Step {index + 1}
                  </div>
                  <div className="font-black text-lg uppercase mb-4">{step.action}</div>
                  <div className="text-xs font-bold text-gray-500 flex justify-between border-t-2 border-gray-100 pt-3">
                    <span className="bg-gray-100 px-1">{step.source_page}</span>
                    <ChevronRight className="h-4 w-4 text-black mx-1"  />
                    <span className="bg-gray-100 px-1">{step.target_page}</span>
                  </div>
                </div>
                {index < wf.steps.length - 1 && (
                  <div className="hidden md:block flex-grow border-t-4 border-dashed border-black relative top-0 mx-2">
                    <span className="absolute -right-2 -top-2.5 h-4 w-4 bg-white border-2 border-black rotate-45"></span>
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
