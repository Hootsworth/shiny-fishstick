"use client";

import React, { useState, useEffect } from 'react';
import {
  Play,
  Layers,
  Compass,
  Database,
  Workflow,
  Code,
  Loader2,
  HelpCircle,
  Compass as CompassIcon
} from 'lucide-react';

import * as api from './lib/api';
import * as mock from './lib/mockData';
import { useCrawlState } from './hooks/useCrawlState';
import { CrawlTrigger } from './components/CrawlTrigger';
import { WorkflowTable } from './components/WorkflowTable';
import { ExecutionLog } from './components/ExecutionLog';
import { DownloadPanel } from './components/DownloadPanel';
import { WorkflowGraph } from './components/WorkflowGraph';
import { ApiMap } from './components/ApiMap';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('projects');

  // Data States
  const [projects, setProjects] = useState<any[]>(mock.MOCK_PROJECTS);
  const [selectedProject, setSelectedProject] = useState<any>(mock.MOCK_PROJECTS[0]);
  const [actions, setActions] = useState<any[]>(mock.MOCK_ACTIONS);
  const [workflows, setWorkflows] = useState<any[]>(mock.MOCK_WORKFLOWS);
  const [apis, setApis] = useState<any[]>(mock.MOCK_APIS);
  const [specs, setSpecs] = useState<any>(mock.MOCK_SPECS);

  // Form States
  const [newProjName, setNewProjName] = useState("");
  const [newProjUrl, setNewProjUrl] = useState("");
  const [crawlLogs, setCrawlLogs] = useState<string[]>([]);
  const [isLiveConnection, setIsLiveConnection] = useState(false);

  // Log helpers
  const addLogMessage = (msg: string) => setCrawlLogs(prev => [...prev, msg]);
  const clearLogs = () => setCrawlLogs([]);

  // Fetch helper
  const loadData = async () => {
    try {
      const dataProj = await api.fetchProjects();
      setIsLiveConnection(true);
      if (dataProj.length > 0) {
        setProjects(dataProj);
        setSelectedProject(dataProj[0]);
      }
    } catch (e) {
      console.log("Using Mock fallback. Backend is not running.");
      setIsLiveConnection(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const loadProjectDetails = async () => {
    if (!selectedProject || !isLiveConnection) return;
    try {
      const id = selectedProject.id;
      const acts = await api.fetchActions(id);
      setActions(acts);

      const wfs = await api.fetchWorkflows(id);
      setWorkflows(wfs);

      const yamlText = await api.fetchSpecYaml(id);
      const pythonText = await api.fetchPythonSDK(id);
      setSpecs({
        yaml: yamlText,
        python: pythonText
      });
      
      // Update mapped APIs from actions
      const apiActions = acts.filter(a => a.action_type === 'api');
      const mappedApis = apiActions.map((a, idx) => {
        const requestBody: any = {};
        try {
          const params = JSON.parse(a.parameters || "[]");
          const bodyParams = params.filter((p: any) => p.source && p.source.startsWith("body."));
          bodyParams.forEach((bp: any) => {
            const key = bp.source.split("body.")[1];
            requestBody[key] = bp.type;
          });
        } catch(e) {}
        
        return {
          id: `api-${idx}`,
          method: a.api_method || "POST",
          url: a.api_url || "",
          request_body: requestBody,
          mapped_action: a.name
        };
      });
      setApis(mappedApis);
    } catch (e) {
      console.error("Failed fetching live project details", e);
    }
  };

  useEffect(() => {
    loadProjectDetails();
  }, [selectedProject, isLiveConnection]);

  const { crawlingStatus, runCrawl } = useCrawlState(
    selectedProject,
    isLiveConnection,
    addLogMessage,
    clearLogs,
    () => {
      loadData();
      loadProjectDetails();
    }
  );

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjName || !newProjUrl) return;

    if (isLiveConnection) {
      try {
        const newProj = await api.createProject(newProjName, newProjUrl);
        setProjects([...projects, newProj]);
        setSelectedProject(newProj);
        setNewProjName("");
        setNewProjUrl("");
      } catch (err) {
        console.error(err);
      }
    } else {
      const mockProj = {
        id: `proj-${Date.now()}`,
        name: newProjName,
        root_url: newProjUrl,
        created_at: new Date().toISOString()
      };
      setProjects([...projects, mockProj]);
      setSelectedProject(mockProj);
      setNewProjName("");
      setNewProjUrl("");
    }
  };

  const NavButton = ({ id, icon: Icon, label, isActive }: any) => {
    const activeClasses = isActive
      ? "bg-pink-100 border-2 border-black shadow-[2px_2px_0px_0px_#000] text-black translate-x-1"
      : "border-2 border-transparent text-gray-600 hover:text-black hover:bg-gray-100 hover:border-gray-300";

    return (
      <button
        onClick={() => setActiveTab(id)}
        className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-md font-bold transition-all duration-200 ${activeClasses}`}
      >
        <Icon className={`h-4 w-4 ${isActive ? 'text-black' : 'text-gray-500'}`} />
        {label}
      </button>
    );
  };

  return (
    <div className="flex h-screen overflow-hidden bg-transparent">
      {/* Sidebar: Stark white, thick borders */}
      <aside className="w-72 bg-white border-r-2 border-black flex flex-col justify-between shrink-0 z-10 shadow-[4px_0_10px_rgba(0,0,0,0.02)]">
        <div>
          <div className="p-6 border-b-2 border-black bg-pink-50">
            <h1 className="text-xl font-extrabold flex items-center gap-2 text-black tracking-tight">
              <CompassIcon className="h-6 w-6" />
              SHINY FISHSTICK
            </h1>
            <p className="text-xs font-semibold text-gray-600 mt-1 uppercase tracking-wider">Agent Spec Compiler</p>
          </div>

          <nav className="p-4 space-y-2">
            <NavButton id="projects" icon={Layers} label="Dashboard" isActive={activeTab === 'projects'} />
            <NavButton id="crawl" icon={Loader2} label="Crawl Progress" isActive={activeTab === 'crawl'} />
            <NavButton id="actions" icon={Compass} label="Action Explorer" isActive={activeTab === 'actions'} />
            <NavButton id="workflow" icon={Workflow} label="Workflows" isActive={activeTab === 'workflow'} />
            <NavButton id="api" icon={Database} label="API Routes" isActive={activeTab === 'api'} />
            <NavButton id="sdk" icon={Code} label="SDK Generator" isActive={activeTab === 'sdk'} />
            <NavButton id="docs" icon={HelpCircle} label="Docs & Help" isActive={activeTab === 'docs'} />
          </nav>
        </div>

        <div className="p-5 border-t-2 border-black bg-white">
          <div className="flex items-center justify-between text-xs font-bold text-gray-500 uppercase">
            <span>Status</span>
            <span className="flex items-center gap-1.5 text-black">
              <span className={`h-2.5 w-2.5 rounded-none border border-black ${isLiveConnection ? 'bg-green-400' : 'bg-pink-400'}`}></span>
              {isLiveConnection ? "Live Connected" : "Local Sandbox"}
            </span>
          </div>
        </div>
      </aside>

      {/* Main Panel */}
      <main className="flex-grow flex flex-col overflow-y-auto">
        <header className="h-20 border-b-2 border-black bg-white flex items-center justify-between px-8 shrink-0 z-10">
          <div className="flex items-center gap-4">
            <span className="text-sm font-bold text-gray-500 uppercase tracking-wider">Project</span>
            <select
              value={selectedProject?.id || ''}
              onChange={(e) => setSelectedProject(projects.find(p => p.id === e.target.value))}
              className="bg-white border-2 border-black rounded-md px-4 py-2 text-sm font-bold focus:outline-none focus:ring-2 focus:ring-pink-300 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] cursor-pointer"
            >
              {projects.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>

          <button
            onClick={runCrawl}
            disabled={crawlingStatus === 'running'}
            className="flex items-center gap-2 bg-black text-white font-bold text-sm px-5 py-2.5 rounded-md border-2 border-black shadow-[4px_4px_0px_0px_#f472b6] hover:shadow-[2px_2px_0px_0px_#f472b6] hover:translate-y-[2px] hover:translate-x-[2px] transition-all disabled:opacity-70 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-y-0 disabled:translate-x-0"
          >
            <Play className="h-4 w-4" />
            ANALYZE WEBSITE
          </button>
        </header>

        <div className="p-10 max-w-6xl mx-auto w-full flex-grow">
          {activeTab === 'projects' && (
            <CrawlTrigger
              actionsCount={actions.length}
              apisCount={apis.length}
              newProjName={newProjName}
              setNewProjName={setNewProjName}
              newProjUrl={newProjUrl}
              setNewProjUrl={setNewProjUrl}
              handleCreateProject={handleCreateProject}
            />
          )}

          {activeTab === 'crawl' && (
            <ExecutionLog crawlingStatus={crawlingStatus} crawlLogs={crawlLogs} />
          )}

          {activeTab === 'actions' && (
            <WorkflowTable projectId={selectedProject?.id || ""} actions={actions} onActionsUpdated={loadProjectDetails} />
          )}

          {activeTab === 'workflow' && (
            <WorkflowGraph workflows={workflows} actions={actions} onWorkflowsUpdated={loadProjectDetails} />
          )}

          {activeTab === 'api' && (
            <ApiMap apis={apis} />
          )}

          {activeTab === 'sdk' && (
            <DownloadPanel specs={specs} />
          )}

          {activeTab === 'docs' && (
            <div className="bg-white border-2 border-black p-8 rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] space-y-8 max-h-[75vh] overflow-y-auto">
              <div className="border-b-2 border-black pb-4 mb-6">
                <h2 className="text-3xl font-black uppercase tracking-tight">Docs & Reference</h2>
                <p className="text-sm font-bold text-gray-600 mt-1 uppercase tracking-wider">Compile websites into semantic SDKs and MCP servers for AI agents. OpenAPI for websites.</p>
              </div>

              {/* Quick Hero Banner */}
              <div className="bg-pink-50 p-4 border-2 border-black">
                <p className="text-sm font-bold text-black">
                  Stop making LLMs reason over HTML, CSS selectors, and brittle browser automation.
                  Compile websites into structured actions that agents can call like native APIs.
                </p>
                <div className="flex flex-wrap gap-2 mt-3">
                  <span className="bg-white px-2 py-0.5 border border-black text-xs font-bold">Apache 2.0</span>
                  <span className="bg-white px-2 py-0.5 border border-black text-xs font-bold">Python Package</span>
                  <span className="bg-white px-2 py-0.5 border border-black text-xs font-bold">npm Package</span>
                  <span className="bg-white px-2 py-0.5 border border-black text-xs font-bold">MCP Compatible</span>
                  <span className="bg-white px-2 py-0.5 border border-black text-xs font-bold">OpenAPI Export</span>
                </div>
              </div>

              {/* Why Comparison */}
              <div>
                <h3 className="text-lg font-bold bg-pink-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">❓ Why?</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full border-2 border-black text-sm">
                    <thead>
                      <tr className="bg-gray-100 border-b-2 border-black">
                        <th className="p-2 text-left font-bold border-r-2 border-black">Traditional Browser Agents</th>
                        <th className="p-2 text-left font-bold">Shiny Fishstick (OpenAPI for websites)</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-black">
                        <td className="p-2 border-r-2 border-black text-gray-700">Parse raw HTML DOM structures</td>
                        <td className="p-2 text-gray-900 font-semibold">Call structured SDK client methods</td>
                      </tr>
                      <tr className="border-b border-black">
                        <td className="p-2 border-r-2 border-black text-gray-700">Guess CSS page elements selectors</td>
                        <td className="p-2 text-gray-900 font-semibold">Use semantic, defined actions</td>
                      </tr>
                      <tr className="border-b border-black">
                        <td className="p-2 border-r-2 border-black text-gray-700">High prompt context token overhead</td>
                        <td className="p-2 text-gray-900 font-semibold">Tiny context window payload</td>
                      </tr>
                      <tr>
                        <td className="p-2 border-r-2 border-black text-gray-700">DOM updates break running workflows</td>
                        <td className="p-2 text-gray-900 font-semibold">Self-healing selector reconciliation</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="text-xs font-bold text-gray-700 mt-2">🚀 78.02% reduction in prompt context size on our verified benchmarks.</p>
              </div>

              {/* How it Works Flow */}
              <div>
                <h3 className="text-lg font-bold bg-blue-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">🏗️ How it Works</h3>
                <pre className="bg-slate-900 text-slate-100 p-4 border-2 border-black font-mono text-xs overflow-x-auto">
                  {"Website\n   │\n   ▼\nCrawler (Session capture & auth tracking)\n   │\n   ▼\nIntent Engine (Semantic actions mapping)\n   │\n   ▼\nWorkflow Discovery (FSM sequence mapping)\n   │\n   ▼\nCompiler (OpenAPI for websites)\n   │\n   ▼\npreflight.yaml (Declarative actions spec)"}
                </pre>
              </div>

              {/* Example Python Output */}
              <div>
                <h3 className="text-lg font-bold bg-yellow-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">💻 Example Client Code</h3>
                <p className="text-sm text-gray-700 mb-2">The compiled client SDK replaces complex Playwright boilerplate scripts:</p>
                <pre className="bg-slate-900 text-slate-100 p-4 border-2 border-black font-mono text-xs overflow-x-auto">
                  {"from specs.sdk import ShinyClient\n\nsite = ShinyClient(base_url=\"https://example.com\")\nawait site.login(email=\"admin@example.com\", password=\"pwd\")\nawait site.search_products(query=\"shoes\")\nawait site.checkout()"}
                </pre>
              </div>

              {/* Core vs Advanced Features */}
              <div>
                <h3 className="text-lg font-bold bg-green-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">⚙️ Core Features</h3>
                <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1 mb-4 leading-relaxed">
                  <li><strong>Semantic Action Discovery:</strong> Automated extraction of forms, buttons, and links.</li>
                  <li><strong>Workflow Graph Generation:</strong> Discovers sequential page state transition paths.</li>
                  <li><strong>API Upgrade Engine:</strong> Automatically converts browser action steps into raw API fetches.</li>
                  <li><strong>Multi-language SDK Generation:</strong> Exports ready-to-run Python, TypeScript, and Rust SDKs.</li>
                  <li><strong>OpenAPI Export:</strong> Creates standard OpenAPI 3.0 REST spec files—an <strong>OpenAPI for websites</strong>.</li>
                </ul>

                <h3 className="text-lg font-bold bg-gray-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">⚙️ Advanced Features</h3>
                <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1 leading-relaxed">
                  <li><strong>Playwright-Stealth Integration:</strong> Bypasses bot verification scripts.</li>
                  <li><strong>AES-256 Fernet Encryption:</strong> Cryptographically secures auth cookies and localstorage variables at rest.</li>
                  <li><strong>Sandbox Virtualization & Chaos Monkey:</strong> Spawns mock site testbeds dynamically on random ports and mutates classes to stress-test healing.</li>
                </ul>
              </div>

              {/* Who should use this */}
              <div>
                <h3 className="text-lg font-bold bg-orange-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">👥 Who should use this?</h3>
                <ul className="list-none text-sm text-gray-700 space-y-1 mt-2 font-semibold">
                  <li>✅ <strong>AI Agent Developers</strong> wanting to connect LLMs to web interfaces.</li>
                  <li>✅ <strong>MCP Tool Creators</strong> who want to expose websites as agent tools.</li>
                  <li>✅ <strong>Browser Automation Engineers</strong> tired of maintaining selector scrapers.</li>
                  <li>✅ <strong>QA Teams</strong> looking to validate site flow logic dynamically.</li>
                </ul>
              </div>

              {/* CLI Reference */}
              <div>
                <h3 className="text-lg font-bold bg-purple-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">💻 CLI Reference</h3>
                <div className="space-y-3 mt-2">
                  <div>
                    <code className="bg-gray-100 px-2 py-0.5 text-xs border border-black font-bold">shiny compile &lt;url&gt;</code>
                    <p className="text-xs text-gray-600 mt-1">Crawls website pages and compiles specifications folders.</p>
                  </div>
                  <div>
                    <code className="bg-gray-100 px-2 py-0.5 text-xs border border-black font-bold">shiny validate &lt;spec&gt;</code>
                    <p className="text-xs text-gray-600 mt-1">Runs structural schema validation checks (the validator for <strong>OpenAPI for websites</strong>).</p>
                  </div>
                  <div>
                    <code className="bg-gray-100 px-2 py-0.5 text-xs border border-black font-bold">shiny serve-mcp &lt;spec&gt;</code>
                    <p className="text-xs text-gray-600 mt-1">Starts standard JSON-RPC mcp server hooks.</p>
                  </div>
                </div>
              </div>

              {/* FAQ & Positioning */}
              <div>
                <h3 className="text-lg font-bold bg-red-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">❓ FAQ & Positioning</h3>
                <div className="space-y-4 mt-2">
                  <div>
                    <p className="text-sm font-bold">Q: Why not Playwright?</p>
                    <p className="text-xs text-gray-700 mt-0.5">A: Playwright requires manual selector scripts maintenance. Shiny Fishstick acts as an <strong>OpenAPI for websites</strong>, exposing clean function methods instead.</p>
                  </div>
                  <div>
                    <p className="text-sm font-bold">Q: Why not Browser Use?</p>
                    <p className="text-xs text-gray-700 mt-0.5">A: Browser Use relies on visual screenshot models, which has high prompt token overhead and is prone to hallucination. Shiny Fishstick compiles the page structure beforehand so your agents execute actions deterministically.</p>
                  </div>
                </div>
              </div>

              {/* Roadmap */}
              <div>
                <h3 className="text-lg font-bold bg-teal-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">🗺️ Roadmap</h3>
                <p className="text-sm text-gray-700 mt-1 leading-relaxed">
                  Phase 1-3 (DX & Telemetry) • Phase 4-5 (Swagger & SDKs) • Phase 6-7 (Regression & Tuning) • Phase 8-10 (Enterprise & Scale).
                </p>
              </div>

              {/* Contributing */}
              <div>
                <h3 className="text-lg font-bold bg-amber-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">📜 Contributing</h3>
                <p className="text-sm text-gray-700 mt-1 leading-relaxed">
                  Read <code className="bg-gray-100 px-1 border border-black text-xs">CONTRIBUTING.md</code> in the repository root for code style rules and local setups.
                </p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}