"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Play,
  Layers,
  Compass,
  Database,
  Workflow,
  Code,
  Loader2,
  HelpCircle,
  Moon,
  Sun,
  Home,
  ArrowLeft
} from 'lucide-react';

import * as api from '../lib/api';
import * as mock from '../lib/mockData';
import { useCrawlState } from '../hooks/useCrawlState';
import { CrawlTrigger } from '../components/CrawlTrigger';
import { WorkflowTable } from '../components/WorkflowTable';
import { ExecutionLog } from '../components/ExecutionLog';
import { DownloadPanel } from '../components/DownloadPanel';
import { WorkflowGraph } from '../components/WorkflowGraph';
import { ApiMap } from '../components/ApiMap';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('projects');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

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

  // Initialize theme
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    const initialTheme = savedTheme || 'light';
    setTheme(initialTheme);
    document.documentElement.setAttribute('data-theme', initialTheme);
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
    localStorage.setItem('theme', nextTheme);
    document.documentElement.setAttribute('data-theme', nextTheme);
  };

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
      ? "bg-[var(--ink)] text-[var(--cream)] font-bold shadow-sm"
      : "text-[var(--ink-soft)] hover:text-[var(--ink)] hover:bg-[var(--cream)] bg-transparent";

    return (
      <button
        onClick={() => setActiveTab(id)}
        className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold uppercase tracking-wider transition-all duration-150 ${activeClasses}`}
      >
        <Icon className="h-4 w-4 shrink-0" />
        <span>{label}</span>
      </button>
    );
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[var(--cream)]">
      {/* Sidebar: Styled clean, rounded paper container, thin line borders */}
      <aside className="w-72 bg-[var(--paper)] border-r border-[var(--line)] flex flex-col justify-between shrink-0 z-10">
        <div>
          {/* Sidebar Header */}
          <div className="p-6 border-b border-[var(--line)] flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2.5 text-[var(--ink)] hover:opacity-85 transition">
              <svg width="20" height="20" viewBox="0 0 100 100" className="text-[var(--pie-green)] fill-current">
                <path d="M50,50 L50,10 A40,40 0 1,1 10,50 L50,50 Z" />
              </svg>
              <h1 className="text-sm font-black uppercase tracking-tight">PREFLIGHT</h1>
            </Link>
            
            <Link href="/" className="p-1.5 rounded-full hover:bg-[var(--cream)] text-[var(--ink-soft)] hover:text-[var(--ink)] transition">
              <Home className="h-4.5 w-4.5" />
            </Link>
          </div>

          {/* Navigation Pill Lists */}
          <nav className="p-4 space-y-1.5">
            <NavButton id="projects" icon={Layers} label="Console Home" isActive={activeTab === 'projects'} />
            <NavButton id="crawl" icon={Loader2} label="Scraper Logs" isActive={activeTab === 'crawl'} />
            <NavButton id="actions" icon={Compass} label="Action Explorer" isActive={activeTab === 'actions'} />
            <NavButton id="workflow" icon={Workflow} label="FSM Workflows" isActive={activeTab === 'workflow'} />
            <NavButton id="api" icon={Database} label="Discovered APIs" isActive={activeTab === 'api'} />
            <NavButton id="sdk" icon={Code} label="SDK Exports" isActive={activeTab === 'sdk'} />
            <NavButton id="docs" icon={HelpCircle} label="Docs & Help" isActive={activeTab === 'docs'} />
          </nav>
        </div>

        {/* Sidebar Footer details */}
        <div className="p-4 border-t border-[var(--line)] space-y-4">
          <div className="flex items-center justify-between text-[10px] font-semibold text-[var(--ink-soft)] uppercase tracking-wider">
            <span>Server</span>
            <span className="flex items-center gap-1.5 text-[var(--ink)] font-bold">
              <span className={`h-2 w-2 rounded-full ${isLiveConnection ? 'bg-[var(--pie-green)]' : 'bg-red-400'}`}></span>
              {isLiveConnection ? "Connected" : "Mock Sandbox"}
            </span>
          </div>

          <div className="flex items-center justify-between gap-2 pt-2 border-t border-[var(--line)] border-dashed">
            <button 
              onClick={toggleTheme} 
              className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wider bg-[var(--cream)] hover:bg-opacity-80 px-3.5 py-2 rounded-full border border-[var(--line)] text-[var(--ink)] transition w-full justify-center"
            >
              {theme === 'light' ? (
                <>
                  <Moon className="h-3.5 w-3.5" />
                  <span>Dark Mode</span>
                </>
              ) : (
                <>
                  <Sun className="h-3.5 w-3.5" />
                  <span>Light Mode</span>
                </>
              )}
            </button>
          </div>
        </div>
      </aside>

      {/* Main Panel Content */}
      <main className="flex-grow flex flex-col overflow-y-auto">
        {/* Header toolbar */}
        <header className="h-20 border-b border-[var(--line)] bg-[var(--paper)] flex items-center justify-between px-8 shrink-0 z-10">
          <div className="flex items-center gap-4">
            <span className="text-xs font-bold text-[var(--ink-soft)] uppercase tracking-wider">Selected Target</span>
            <select
              value={selectedProject?.id || ''}
              onChange={(e) => setSelectedProject(projects.find(p => p.id === e.target.value))}
              className="bg-[var(--cream)] border border-[var(--line)] rounded-full px-4 py-2 text-xs font-semibold text-[var(--ink)] focus:outline-none focus:ring-1 focus:ring-[var(--pie-green)] cursor-pointer"
            >
              {projects.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>

          <button
            onClick={runCrawl}
            disabled={crawlingStatus === 'running'}
            className="flex items-center gap-2 bg-[var(--ink)] hover:bg-[var(--pie-green)] hover:text-[var(--ink)] text-[var(--cream)] font-bold text-xs uppercase px-5 py-3 rounded-full border border-[var(--line)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="h-3.5 w-3.5 fill-current" />
            <span>Crawl Website</span>
          </button>
        </header>

        {/* Inner container wrapper */}
        <div className="p-8 max-w-[1180px] w-full mx-auto flex-grow">
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
            <div className="bg-[var(--paper)] border border-[var(--line)] p-8 rounded-[24px] shadow-sm space-y-8 max-h-[75vh] overflow-y-auto">
              <h2 className="display-title text-2xl mb-6 text-[var(--ink)]">Docs & Reference</h2>
              
              {/* Getting Started */}
              <div className="space-y-3">
                <h3 className="text-sm font-bold bg-[var(--cream)] px-4 py-2 border border-[var(--line)] rounded-full inline-block uppercase tracking-wider text-[var(--ink)]">🚀 Getting Started (5 Minutes)</h3>
                <p className="text-xs text-[var(--ink-soft)] leading-relaxed">
                  Shiny Fishstick turns websites into agent-callable action specs in under 5 minutes:
                </p>
                <pre className="bg-[var(--code-bg)] text-[var(--code-text)] p-4 rounded-[16px] font-mono text-xs overflow-x-auto border border-[var(--line)]">
                  {"# 1. Initialize environment setup\nmake setup\n\n# 2. Run all verification tests\nmake test\n\n# 3. Run the compiler demo pipeline\nmake demo"}
                </pre>
              </div>

              {/* Architecture */}
              <div className="space-y-3">
                <h3 className="text-sm font-bold bg-[var(--cream)] px-4 py-2 border border-[var(--line)] rounded-full inline-block uppercase tracking-wider text-[var(--ink)]">🏗️ Architecture</h3>
                <ul className="list-disc pl-5 text-xs text-[var(--ink-soft)] space-y-2 leading-relaxed">
                  <li><strong>Crawler Service:</strong> Handles dynamic browser authentication log-ins and captures secure session states.</li>
                  <li><strong>Workflow Builder:</strong> Translates DOM form submissions into FSM transition diagrams.</li>
                  <li><strong>Spec Exporter:</strong> Compiles actions lists into Swagger OpenAPI definitions and Client SDK packages.</li>
                  <li><strong>UI Chaos Monkey:</strong> Mutates HTML selector classes and injects latency to verify locator self-healing resilience.</li>
                </ul>
              </div>

              {/* CLI Reference */}
              <div className="space-y-3">
                <h3 className="text-sm font-bold bg-[var(--cream)] px-4 py-2 border border-[var(--line)] rounded-full inline-block uppercase tracking-wider text-[var(--ink)]">💻 CLI Reference</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-[var(--cream)] rounded-[16px] border border-[var(--line)]">
                    <code className="text-[11px] font-mono font-bold text-[var(--ink)]">shiny compile &lt;url&gt; --out &lt;dir&gt;</code>
                    <p className="text-[10px] text-[var(--ink-soft)] mt-1.5">Crawls website pages and compiles specifications folders.</p>
                  </div>
                  <div className="p-4 bg-[var(--cream)] rounded-[16px] border border-[var(--line)]">
                    <code className="text-[11px] font-mono font-bold text-[var(--ink)]">shiny inspect &lt;spec&gt;</code>
                    <p className="text-[10px] text-[var(--ink-soft)] mt-1.5">Reads and prints compiled actions list.</p>
                  </div>
                  <div className="p-4 bg-[var(--cream)] rounded-[16px] border border-[var(--line)]">
                    <code className="text-[11px] font-mono font-bold text-[var(--ink)]">shiny validate &lt;spec&gt;</code>
                    <p className="text-[10px] text-[var(--ink-soft)] mt-1.5">Runs structural schema validation checks.</p>
                  </div>
                  <div className="p-4 bg-[var(--cream)] rounded-[16px] border border-[var(--line)]">
                    <code className="text-[11px] font-mono font-bold text-[var(--ink)]">shiny serve-mcp &lt;spec&gt;</code>
                    <p className="text-[10px] text-[var(--ink-soft)] mt-1.5">Starts standard JSON-RPC mcp server hooks.</p>
                  </div>
                </div>
              </div>

              {/* Examples */}
              <div className="space-y-3">
                <h3 className="text-sm font-bold bg-[var(--cream)] px-4 py-2 border border-[var(--line)] rounded-full inline-block uppercase tracking-wider text-[var(--ink)]">📁 Examples</h3>
                <p className="text-xs text-[var(--ink-soft)] leading-relaxed">
                  Sample templates are stored under <code className="bg-[var(--cream)] px-2 py-0.5 rounded border border-[var(--line)] text-xs font-mono text-[var(--ink)]">/examples/</code>:
                </p>
                <ul className="list-disc pl-5 text-xs text-[var(--ink-soft)] space-y-1">
                  <li><strong>ecommerce/preflight.yaml</strong>: Catalogue cart checkout actions.</li>
                  <li><strong>saas-dashboard/preflight.yaml</strong>: SaaS monitoring filter table metrics.</li>
                  <li><strong>mcp-agent/agent.py</strong>: Demo code showing agent connections.</li>
                </ul>
              </div>

              {/* FAQ */}
              <div className="space-y-3">
                <h3 className="text-sm font-bold bg-[var(--cream)] px-4 py-2 border border-[var(--line)] rounded-full inline-block uppercase tracking-wider text-[var(--ink)]">❓ FAQ</h3>
                <div className="space-y-3 mt-2 text-xs">
                  <p className="font-bold text-[var(--ink)]">Q: Why not just Playwright?</p>
                  <p className="text-[var(--ink-soft)]">A: Playwright is lower-level. Shiny Fishstick compiles websites into semantic actions (e.g. `checkout()`) so agents can call them natively.</p>
                  <p className="font-bold text-[var(--ink)]">Q: Are credentials database rows secure?</p>
                  <p className="text-[var(--ink-soft)]">A: Yes, cookies and localStorage sessions are encrypted at rest using AES-256 Fernet keys.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
