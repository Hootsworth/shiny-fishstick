import React from 'react';
import { Layers, Plus } from 'lucide-react';

interface CrawlTriggerProps {
  actionsCount: number;
  apisCount: number;
  newProjName: string;
  setNewProjName: (v: string) => void;
  newProjUrl: string;
  setNewProjUrl: (v: string) => void;
  handleCreateProject: (e: React.FormEvent) => void;
}

export function CrawlTrigger({
  actionsCount,
  apisCount,
  newProjName,
  setNewProjName,
  newProjUrl,
  setNewProjUrl,
  handleCreateProject,
}: CrawlTriggerProps) {
  return (
    <div className="space-y-10">
      <div>
        <h2 className="text-3xl font-black tracking-tight flex items-center gap-3 text-black">
          <Layers className="h-8 w-8" />
          PROJECT METRICS
        </h2>
        <p className="text-gray-600 font-medium mt-2">Overview of compiled agent schemas.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Discovered Actions', val: actionsCount, desc: 'Semantic capabilities' },
          { label: 'Mapped APIs', val: apisCount, desc: 'Optimized endpoints' },
          { label: 'Spec Health', val: '98%', desc: 'Selector confidence' }
        ].map((stat, i) => (
          <div key={i} className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-md p-6 relative overflow-hidden">
            <div className="text-black text-xs font-bold uppercase tracking-widest">{stat.label}</div>
            <div className="text-4xl font-black mt-3 text-black">{stat.val}</div>
            <p className="text-sm font-semibold text-gray-500 mt-2">{stat.desc}</p>
            <div className="absolute -bottom-4 -right-4 w-16 h-16 bg-pink-100 rounded-full z-[-1] border-2 border-black opacity-50"></div>
          </div>
        ))}
      </div>

      <div className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-md p-8 max-w-xl">
        <h3 className="text-xl font-black mb-6 flex items-center gap-2">
          <Plus className="text-black h-6 w-6" />
          ADD NEW TARGET
        </h3>
        <form onSubmit={handleCreateProject} className="space-y-5">
          <div>
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">Target Name</label>
            <input
              type="text"
              value={newProjName}
              onChange={(e) => setNewProjName(e.target.value)}
              placeholder="My Store Website"
              className="w-full bg-gray-50 border-2 border-black rounded-md px-4 py-3 text-black font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-pink-300"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">Root URL</label>
            <input
              type="url"
              value={newProjUrl}
              onChange={(e) => setNewProjUrl(e.target.value)}
              placeholder="http://localhost:8001"
              className="w-full bg-gray-50 border-2 border-black rounded-md px-4 py-3 text-black font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-pink-300"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-black text-white font-bold py-3 rounded-md border-2 border-black shadow-[4px_4px_0px_0px_#f472b6] hover:shadow-[2px_2px_0px_0px_#f472b6] hover:translate-y-[2px] hover:translate-x-[2px] transition-all uppercase tracking-wider mt-2"
          >
            Create Project
          </button>
        </form>
      </div>
    </div>
  );
}
