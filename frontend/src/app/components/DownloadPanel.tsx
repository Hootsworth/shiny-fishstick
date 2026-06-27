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
          <h2 className="text-3xl font-black tracking-tight flex items-center gap-3">
            <Code className="h-8 w-8" />
            COMPILED ASSETS
          </h2>
          <p className="text-gray-600 font-medium mt-2">Ready-to-use specifications and language wrappers.</p>
        </div>
        <div className="flex gap-4">
          <button
            onClick={() => downloadFile(specs.yaml, 'preflight.yaml')}
            className="flex items-center gap-2 bg-white text-black border-2 border-black px-4 py-2 font-black text-sm uppercase tracking-wider shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-y-[2px] hover:translate-x-[2px] transition-all"
          >
            <Download className="h-4 w-4" />
            YAML Spec
          </button>
          <button
            onClick={() => downloadFile(specs.python, 'sdk.py')}
            className="flex items-center gap-2 bg-white text-black border-2 border-black px-4 py-2 font-black text-sm uppercase tracking-wider shadow-[4px_4px_0px_0px_#f472b6] hover:shadow-[2px_2px_0px_0px_#f472b6] hover:translate-y-[2px] hover:translate-x-[2px] transition-all"
          >
            <Download className="h-4 w-4 text-pink-500" />
            Python SDK
          </button>
        </div>
      </div>

      {/* Code Previews */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <div className="space-y-3">
          <div className="text-sm font-black uppercase tracking-widest flex items-center gap-2 bg-gray-100 p-3 border-2 border-black border-b-0">
            <FileText className="h-4 w-4" />
            preflight.yaml
          </div>
          <pre className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-6 overflow-auto text-sm font-mono font-bold h-[500px]">
            {specs.yaml}
          </pre>
        </div>

        <div className="space-y-3">
          <div className="text-sm font-black uppercase tracking-widest flex items-center gap-2 bg-pink-100 p-3 border-2 border-black border-b-0">
            <Code className="h-4 w-4" />
            sdk.py
          </div>
          <pre className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-6 overflow-auto text-sm font-mono font-bold h-[500px]">
            {specs.python}
          </pre>
        </div>
      </div>
    </div>
  );
}
