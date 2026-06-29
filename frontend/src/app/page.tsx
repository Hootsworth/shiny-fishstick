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
              <h2 className="text-3xl font-black mb-6 uppercase tracking-tight">Docs & Reference</h2>
              
              {/* Getting Started (5 minutes) */}
              <div>
                <h3 className="text-lg font-bold bg-pink-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">🚀 Getting Started (5 Minutes)</h3>
                <p className="text-sm text-gray-700 mt-2 mb-2 leading-relaxed">
                  Shiny Fishstick turns websites into agent-callable action specs in under 5 minutes:
                </p>
                <pre className="bg-slate-900 text-slate-100 p-4 border-2 border-black font-mono text-xs overflow-x-auto">
                  {"# 1. Initialize environment setup\nmake setup\n\n# 2. Run all verification tests\nmake test\n\n# 3. Run the compiler demo pipeline\nmake demo"}
                </pre>
              </div>

              {/* Architecture */}
              <div>
                <h3 className="text-lg font-bold bg-blue-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">🏗️ Architecture</h3>
                <ul className="list-disc pl-5 text-sm text-gray-700 space-y-2 leading-relaxed">
                  <li><strong>Crawler Service:</strong> Handles dynamic browser authentication log-ins and captures secure session states.</li>
                  <li><strong>Workflow Builder:</strong> Translates DOM form submissions into FSM transition diagrams.</li>
                  <li><strong>Spec Exporter:</strong> Compiles actions lists into Swagger OpenAPI definitions and Client SDK packages.</li>
                  <li><strong>UI Chaos Monkey:</strong> Mutates HTML selector classes and injects latency to verify locator self-healing resilience.</li>
                </ul>
              </div>

              {/* CLI Reference */}
              <div>
                <h3 className="text-lg font-bold bg-green-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">💻 CLI Reference</h3>
                <div className="space-y-4">
                  <div>
                    <code className="bg-gray-100 px-2 py-1 text-xs border border-black font-bold">shiny compile &lt;url&gt; --out &lt;dir&gt;</code>
                    <p className="text-xs text-gray-600 mt-1">Crawls website pages and compiles specifications folders.</p>
                  </div>
                  <div>
                    <code className="bg-gray-100 px-2 py-1 text-xs border border-black font-bold">shiny inspect &lt;spec&gt;</code>
                    <p className="text-xs text-gray-600 mt-1">Reads and prints compiled actions list.</p>
                  </div>
                  <div>
                    <code className="bg-gray-100 px-2 py-1 text-xs border border-black font-bold">shiny validate &lt;spec&gt;</code>
                    <p className="text-xs text-gray-600 mt-1">Runs structural schema validation checks.</p>
                  </div>
                  <div>
                    <code className="bg-gray-100 px-2 py-1 text-xs border border-black font-bold">shiny serve-mcp &lt;spec&gt;</code>
                    <p className="text-xs text-gray-600 mt-1">Starts standard JSON-RPC mcp server hooks.</p>
                  </div>
                </div>
              </div>

              {/* Examples */}
              <div>
                <h3 className="text-lg font-bold bg-yellow-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">📁 Examples</h3>
                <p className="text-sm text-gray-700 mt-1 leading-relaxed">
                  Sample templates are stored under <code className="bg-gray-100 px-1 border border-black text-xs">/examples/</code>:
                </p>
                <ul className="list-disc pl-5 text-sm text-gray-700 mt-2 space-y-1">
                  <li><strong>ecommerce/preflight.yaml</strong>: Catalogue cart checkout actions.</li>
                  <li><strong>saas-dashboard/preflight.yaml</strong>: SaaS monitoring filter table metrics.</li>
                  <li><strong>mcp-agent/agent.py</strong>: Demo code showing agent connections.</li>
                </ul>
              </div>

              {/* FAQ */}
              <div>
                <h3 className="text-lg font-bold bg-purple-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">❓ FAQ</h3>
                <div className="space-y-3 mt-2">
                  <p className="text-sm font-bold">Q: Why not just Playwright?</p>
                  <p className="text-xs text-gray-700">A: Playwright is lower-level. Shiny Fishstick compiles websites into semantic actions (e.g. `checkout()`) so agents can call them natively.</p>
                  <p className="text-sm font-bold">Q: Are credentials database rows secure?</p>
                  <p className="text-xs text-gray-700">A: Yes, cookies and localStorage sessions are encrypted at rest using AES-256 Fernet keys.</p>
                </div>
              </div>

              {/* Roadmap */}
              <div>
                <h3 className="text-lg font-bold bg-red-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">🗺️ Roadmap</h3>
                <p className="text-sm text-gray-700 mt-2 leading-relaxed">
                  Milestones include visual pixel regression comparisons, multi-tenant Keycloak RBAC layouts, offline llama.cpp parses, and Tauri clients wrappers.
                </p>
              </div>

              {/* Contributing */}
              <div>
                <h3 className="text-lg font-bold bg-orange-100 p-2 border-2 border-black inline-block uppercase tracking-wider mb-3">📜 Contributing</h3>
                <p className="text-sm text-gray-700 mt-2 leading-relaxed">
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