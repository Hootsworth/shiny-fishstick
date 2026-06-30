import React from 'react';
import { Code, Download, FileText } from 'lucide-react';

interface Specs {
  yaml: string;
  python: string;
}

interface DownloadPanelProps {
  specs: Specs;
}

export function DownloadPanel({ specs }: DownloadPanelProps) {
  const downloadFile = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row justify-between md:items-end gap-6">
        <div>
          <h2 className="display-title text-2xl flex items-center gap-3 text-[var(--ink)]">
            <Code className="h-7 w-7 text-[var(--pie-green-deep)]" />
            <span>Compiled SDKs & Specs</span>
          </h2>
          <p className="text-[var(--ink-soft)] text-xs font-semibold mt-1">Ready-to-use specifications and language wrapper clients.</p>
        </div>
        <div className="flex gap-4">
          <button
            onClick={() => downloadFile(specs.yaml, 'preflight.yaml')}
            className="flex items-center gap-2 bg-[var(--paper)] text-[var(--ink)] border border-[var(--line)] px-5 py-2.5 rounded-full font-bold text-xs uppercase tracking-wider hover:bg-[var(--cream)] transition shadow-sm"
          >
            <Download className="h-4 w-4" />
            YAML Spec
          </button>
          <button
            onClick={() => downloadFile(specs.python, 'sdk.py')}
            className="flex items-center gap-2 bg-[var(--ink)] text-[var(--cream)] border border-[var(--line)] px-5 py-2.5 rounded-full font-bold text-xs uppercase tracking-wider hover:bg-[var(--pie-green)] hover:text-[var(--ink)] transition shadow-sm"
          >
            <Download className="h-4 w-4" />
            Python SDK
          </button>
        </div>
      </div>

      {/* Code Previews */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <div className="space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider flex items-center gap-2 bg-[var(--paper)] p-3.5 border border-[var(--line)] rounded-t-[16px] text-[var(--ink)] border-b-0">
            <FileText className="h-4 w-4 text-[var(--pie-green-deep)]" />
            preflight.yaml
          </div>
          <pre className="bg-[var(--code-bg)] text-[var(--code-text)] border border-[var(--line)] rounded-b-[24px] p-6 overflow-auto text-xs font-mono h-[500px] shadow-sm">
            {specs.yaml}
          </pre>
        </div>

        <div className="space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider flex items-center gap-2 bg-[var(--paper)] p-3.5 border border-[var(--line)] rounded-t-[16px] text-[var(--ink)] border-b-0">
            <Code className="h-4 w-4 text-[var(--pie-green-deep)]" />
            sdk.py
          </div>
          <pre className="bg-[var(--code-bg)] text-[var(--code-text)] border border-[var(--line)] rounded-b-[24px] p-6 overflow-auto text-xs font-mono h-[500px] shadow-sm">
            {specs.python}
          </pre>
        </div>
      </div>
    </div>
  );
}
