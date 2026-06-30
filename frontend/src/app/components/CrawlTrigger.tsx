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
        <h2 className="display-title text-2xl flex items-center gap-3 text-[var(--ink)]">
          <Layers className="h-7 w-7 text-[var(--pie-green-deep)]" />
          <span>Console Metrics</span>
        </h2>
        <p className="text-[var(--ink-soft)] text-xs font-semibold mt-1">Status and compiled target specifications details.</p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Discovered Actions', val: actionsCount, desc: 'Classified browser capabilities' },
          { label: 'Mapped APIs', val: apisCount, desc: 'Bypassed high-speed endpoints' },
          { label: 'Spec Health', val: '98%', desc: 'Dynamic locator confidence' }
        ].map((stat, i) => (
          <div key={i} className="bg-[var(--paper)] border border-[var(--line)] rounded-[24px] p-6 relative overflow-hidden shadow-sm hover:border-[var(--pie-green)] transition duration-200">
            <div className="text-[var(--ink-soft)] text-[10px] font-bold uppercase tracking-wider">{stat.label}</div>
            <div className="text-4xl font-extrabold mt-3 text-[var(--ink)] tracking-tight">{stat.val}</div>
            <p className="text-[11px] text-[var(--ink-soft)] mt-2">{stat.desc}</p>
            {/* Ambient visual badge */}
            <div className="absolute -bottom-4 -right-4 w-12 h-12 bg-[var(--pie-green)] rounded-full z-[0] opacity-10"></div>
          </div>
        ))}
      </div>

      {/* Form section */}
      <div className="bg-[var(--paper)] border border-[var(--line)] rounded-[24px] p-8 max-w-xl shadow-sm">
        <h3 className="text-sm font-bold uppercase tracking-wider text-[var(--ink)] mb-6 flex items-center gap-2">
          <Plus className="text-[var(--pie-green-deep)] h-5 w-5" />
          <span>Register New Target</span>
        </h3>
        <form onSubmit={handleCreateProject} className="space-y-5">
          <div>
            <label className="block text-[10px] font-bold text-[var(--ink-soft)] uppercase tracking-wider mb-2">Target Name</label>
            <input
              type="text"
              value={newProjName}
              onChange={(e) => setNewProjName(e.target.value)}
              placeholder="e.g. Acme Ecommerce Store"
              className="w-full bg-[var(--cream)] border border-[var(--line)] rounded-full px-5 py-3.5 text-xs text-[var(--ink)] focus:outline-none focus:ring-1 focus:ring-[var(--pie-green)]"
            />
          </div>
          <div>
            <label className="block text-[10px] font-bold text-[var(--ink-soft)] uppercase tracking-wider mb-2">Root URL</label>
            <input
              type="url"
              value={newProjUrl}
              onChange={(e) => setNewProjUrl(e.target.value)}
              placeholder="http://localhost:8001"
              className="w-full bg-[var(--cream)] border border-[var(--line)] rounded-full px-5 py-3.5 text-xs text-[var(--ink)] focus:outline-none focus:ring-1 focus:ring-[var(--pie-green)]"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-[var(--ink)] hover:bg-[var(--pie-green)] hover:text-[var(--ink)] text-[var(--cream)] font-bold py-3.5 rounded-full border border-[var(--line)] text-xs uppercase tracking-wider transition-all duration-150 mt-2"
          >
            Create Project
          </button>
        </form>
      </div>
    </div>
  );
}
