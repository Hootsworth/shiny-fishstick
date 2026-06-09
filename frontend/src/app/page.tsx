"use client";

import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Check, 
  Loader2, 
  Code, 
  Workflow, 
  Compass, 
  Database, 
  ShieldAlert, 
  Layers, 
  RefreshCw, 
  Download, 
  Search, 
  FileText, 
  CheckCircle, 
  ExternalLink,
  ChevronRight,
  Sparkles,
  HelpCircle,
  Plus
} from 'lucide-react';

// API root config
const API_BASE = "http://localhost:8000/api";

// High fidelity mock data for instant browseability
const MOCK_PROJECTS = [
  { id: "proj-1", name: "E-Commerce Mock Store", root_url: "http://localhost:8001", created_at: "2026-06-09T18:00:00Z" }
];

const MOCK_CRAWLS = [
  { id: "crawl-1", project_id: "proj-1", status: "completed", started_at: "2026-06-09T18:01:00Z", completed_at: "2026-06-09T18:02:15Z" }
];

const MOCK_ACTIONS = [
  { id: "act-1", name: "login", intent: "login", selector: "#login-form", action_type: "browser", confidence_score: 0.95, description: "Logs in the user with credentials", parameters: JSON.stringify([{name: "email", type: "string", selector: "#email"}, {name: "password", type: "string", selector: "#password"}]) },
  { id: "act-2", name: "search_products", intent: "search", selector: "#search-form", action_type: "browser", confidence_score: 0.95, description: "Searches for products in the store", parameters: JSON.stringify([{name: "q", type: "string", selector: "#search-input"}]) },
  { id: "act-3", name: "add_to_cart", intent: "add_to_cart", selector: "#add-to-cart-btn", action_type: "api", confidence_score: 0.98, description: "Adds the current product to the shopping cart", api_url: "/api/cart/add", api_method: "POST", parameters: JSON.stringify([{name: "product_id", type: "string", selector: ""}, {name: "quantity", type: "integer", selector: ""}]) },
  { id: "act-4", name: "checkout", intent: "checkout", selector: "#checkout-submit-btn", action_type: "browser", confidence_score: 0.90, description: "Proceeds to place the order and checkout", parameters: "[]" }
];

const MOCK_WORKFLOWS = [
  { 
    id: "wf-1", 
    name: "purchase_flow", 
    description: "End-to-end purchasing workflow from login to order confirmation", 
    steps: [
      { action: "login", source_page: "/login", target_page: "/catalog" },
      { action: "search_products", source_page: "/catalog", target_page: "/catalog" },
      { action: "add_to_cart", source_page: "/product/{id}", target_page: "/checkout" },
      { action: "checkout", source_page: "/checkout", target_page: "/catalog" }
    ] 
  }
];

const MOCK_APIS = [
  { id: "api-1", method: "POST", url: "/api/cart/add", request_body: { product_id: "string", quantity: "integer" }, mapped_action: "add_to_cart" }
];

const MOCK_SPECS = {
  yaml: `version: 1.0.0
site: http://localhost:8001
actions:
  login:
    description: Logs in the user with credentials
    action_type: browser
    selector: '#login-form'
    parameters:
    - name: email
      type: string
      required: true
      selector: '#email'
    - name: password
      type: string
      required: true
      selector: '#password'
  search_products:
    description: Searches for products in the store
    action_type: browser
    selector: '#search-form'
    parameters:
    - name: q
      type: string
      required: true
      selector: '#search-input'
  add_to_cart:
    description: Adds the current product to shopping cart
    action_type: api
    selector: '#add-to-cart-btn'
    parameters:
    - name: product_id
      type: string
      required: true
    - name: quantity
      type: integer
      required: true
    api:
      url: /api/cart/add
      method: POST
  checkout:
    description: Proceeds to place the order and checkout
    action_type: browser
    selector: '#checkout-submit-btn'
    parameters: []`,
  python: `# Shiny Fishstick Generated Python SDK
import requests
from playwright.sync_api import sync_playwright

class ShinyFishstickSiteSDK:
    def __init__(self, root_url="http://localhost:8001"):
        self.root_url = root_url
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.session_cookies = None

    def start(self, headless=True):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.goto(self.root_url)
        return self

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def login(self, email, password):
        """Logs in the user with credentials"""
        self.page.goto(self.root_url + "/login")
        self.page.fill("#email", str(email))
        self.page.fill("#password", str(password))
        self.page.click("#login-submit-btn")
        self.page.wait_for_load_state("networkidle")
        self.session_cookies = self.page.context.cookies()

    def search_products(self, q):
        """Searches for products in the store"""
        self.page.goto(self.root_url + "/catalog")
        self.page.fill("#search-input", str(q))
        self.page.click("#search-submit-btn")
        self.page.wait_for_load_state("networkidle")

    def add_to_cart(self, product_id, quantity=1):
        """Adds the current product to shopping cart"""
        session_val = None
        if self.session_cookies:
            session_val = next((c["value"] for c in self.session_cookies if c["name"] == "session"), None)
        headers = {}
        cookies = {}
        if session_val:
            cookies = {"session": session_val}
        payload = {
            "product_id": product_id,
            "quantity": quantity
        }
        res = requests.post(
            self.root_url + "/api/cart/add",
            json=payload,
            cookies=cookies
        )
        return res.json()

    def checkout(self):
        """Proceeds to place the order and checkout"""
        self.page.goto(self.root_url + "/checkout")
        self.page.click("#checkout-submit-btn")
        self.page.wait_for_load_state("networkidle")`
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('projects');
  
  // Data States
  const [projects, setProjects] = useState<any[]>(MOCK_PROJECTS);
  const [selectedProject, setSelectedProject] = useState<any>(MOCK_PROJECTS[0]);
  const [crawls, setCrawls] = useState<any[]>(MOCK_CRAWLS);
  const [actions, setActions] = useState<any[]>(MOCK_ACTIONS);
  const [workflows, setWorkflows] = useState<any[]>(MOCK_WORKFLOWS);
  const [apis, setApis] = useState<any[]>(MOCK_APIS);
  const [specs, setSpecs] = useState<any>(MOCK_SPECS);
  
  // Loading & Form States
  const [loading, setLoading] = useState(false);
  const [crawlingStatus, setCrawlingStatus] = useState<string>("idle"); // idle, pending, running, completed
  const [newProjName, setNewProjName] = useState("");
  const [newProjUrl, setNewProjUrl] = useState("");
  const [crawlLogs, setCrawlLogs] = useState<string[]>([]);
  const [isLiveConnection, setIsLiveConnection] = useState(false);

  // Fetch data from FastAPI backend if online
  useEffect(() => {
    async function loadData() {
      try {
        const resProj = await fetch(`${API_BASE}/projects`);
        if (resProj.ok) {
          const dataProj = await resProj.json();
          setIsLiveConnection(true);
          if (dataProj.length > 0) {
            setProjects(dataProj);
            setSelectedProject(dataProj[0]);
          }
        }
      } catch (e) {
        console.log("Using Mock fallback. Backend is not running.");
        setIsLiveConnection(false);
      }
    }
    loadData();
  }, []);

  // Fetch project-specific details
  useEffect(() => {
    if (!selectedProject || !isLiveConnection) return;
    
    async function loadProjectDetails() {
      try {
        const id = selectedProject.id;
        const resActions = await fetch(`${API_BASE}/projects/${id}/actions`);
        if (resActions.ok) setActions(await resActions.ok ? await resActions.json() : MOCK_ACTIONS);

        const resWorkflows = await fetch(`${API_BASE}/projects/${id}/workflows`);
        if (resWorkflows.ok) setWorkflows(await resWorkflows.json());

        const resSpec = await fetch(`${API_BASE}/projects/${id}/spec`);
        if (resSpec.ok) {
          const yamlText = await resSpec.text();
          const resPython = await fetch(`${API_BASE}/projects/${id}/sdk/python`);
          const pythonText = resPython.ok ? await resPython.text() : MOCK_SPECS.python;
          setSpecs({
            yaml: yamlText,
            python: pythonText
          });
        }
      } catch (e) {
        console.error("Failed fetching live project details", e);
      }
    }
    loadProjectDetails();
  }, [selectedProject, isLiveConnection]);

  // Create Project
  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjName || !newProjUrl) return;

    if (isLiveConnection) {
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE}/projects`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: newProjName, root_url: newProjUrl })
        });
        if (res.ok) {
          const newProj = await res.json();
          setProjects([...projects, newProj]);
          setSelectedProject(newProj);
          setNewProjName("");
          setNewProjUrl("");
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    } else {
      // Mock Creation
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

  // Trigger Crawl
  const triggerCrawl = async () => {
    if (!selectedProject) return;
    setCrawlLogs([]);
    setCrawlingStatus("pending");
    setActiveTab("crawl");

    const logs = [
      `[Crawler] Initializing crawler for ${selectedProject.root_url}...`,
      `[Crawler] Launching Playwright browser instance...`,
      `[Crawler] Visiting seed root URL: ${selectedProject.root_url}...`,
    ];

    setCrawlLogs(logs);

    if (isLiveConnection) {
      try {
        const res = await fetch(`${API_BASE}/projects/${selectedProject.id}/crawl`, { method: 'POST' });
        if (res.ok) {
          const data = await res.json();
          const crawlId = data.crawl_id;
          
          // Poll status
          const interval = setInterval(async () => {
            const statusRes = await fetch(`${API_BASE}/crawls/${crawlId}`);
            if (statusRes.ok) {
              const crawlData = await statusRes.json();
              setCrawlingStatus(crawlData.status);
              
              if (crawlData.status === "running") {
                setCrawlLogs(prev => [
                  ...prev,
                  `[Crawler] Scanning page content dynamically...`,
                  `[Crawler] Extracting inputs, forms, and clickable elements...`
                ]);
              }
              
              if (crawlData.status === "completed" || crawlData.status === "failed") {
                clearInterval(interval);
                // Refresh items
                setIsLiveConnection(prev => !prev); // force reload hook
                setCrawlLogs(prev => [
                  ...prev,
                  `[Crawler] Run finished. Crawl status: ${crawlData.status.toUpperCase()}`,
                  `[Semantic Intent] Running classifications...`,
                  `[API Discovery] Mapped routes to background fetch handlers.`,
                  `[SDK Generator] Specifications regenerated successfully.`
                ]);
              }
            }
          }, 2000);
        }
      } catch (err) {
        setCrawlingStatus("failed");
        console.error(err);
      }
    } else {
      // Mock crawl simulation
      setTimeout(() => {
        setCrawlingStatus("running");
        setCrawlLogs(prev => [
          ...prev,
          `[Crawler] Redirected from ${selectedProject.root_url} to /login (Auth required)`,
          `[Auth Analyzer] Resolving login procedure using simulated cookies...`,
          `[Crawler] Re-evaluating authorized links...`,
          `[Crawler] Discovered pages: [/login, /catalog, /product/{id}, /checkout]`
        ]);
      }, 2000);

      setTimeout(() => {
        setCrawlingStatus("completed");
        setCrawlLogs(prev => [
          ...prev,
          `[DOM Analyzer] Selector generation completed.`,
          `[API Discovery] Successfully mapped action 'add_to_cart' to direct API: POST /api/cart/add`,
          `[SDK Generator] Python, TypeScript wrapper SDKs compiled.`,
          `[Crawler] Compile Finished. Spec ready for download.`
        ]);
      }, 5000);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar with Premium Glassmorphism */}
      <aside className="w-64 bg-slate-950/60 border-r border-slate-800/80 backdrop-blur-lg flex flex-col justify-between shrink-0">
        <div>
          <div className="p-6 border-b border-slate-800/80">
            <h1 className="text-xl font-bold flex items-center gap-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-emerald-400">
              <Compass className="h-6 w-6 text-blue-400 animate-pulse" />
              Shiny Fishstick
            </h1>
            <p className="text-xs text-slate-500 mt-1">AI Browser Agent Spec Compiler</p>
          </div>
          
          <nav className="p-4 space-y-1">
            <button 
              onClick={() => setActiveTab('projects')}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'projects' ? 'bg-indigo-600/20 border-l-2 border-indigo-500 text-indigo-200' : 'text-slate-400 hover:bg-slate-900 hover:text-white'}`}
            >
              <Layers className="h-4 w-4" />
              Project Dashboard
            </button>
            <button 
              onClick={() => setActiveTab('crawl')}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'crawl' ? 'bg-indigo-600/20 border-l-2 border-indigo-500 text-indigo-200' : 'text-slate-400 hover:bg-slate-900 hover:text-white'}`}
            >
              <Loader2 className={`h-4 w-4 ${crawlingStatus === 'running' ? 'animate-spin text-blue-400' : ''}`} />
              Crawl Progress
            </button>
            <button 
              onClick={() => setActiveTab('actions')}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'actions' ? 'bg-indigo-600/20 border-l-2 border-indigo-500 text-indigo-200' : 'text-slate-400 hover:bg-slate-900 hover:text-white'}`}
            >
              <Compass className="h-4 w-4" />
              Action Explorer
            </button>
            <button 
              onClick={() => setActiveTab('workflow')}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'workflow' ? 'bg-indigo-600/20 border-l-2 border-indigo-500 text-indigo-200' : 'text-slate-400 hover:bg-slate-900 hover:text-white'}`}
            >
              <Workflow className="h-4 w-4" />
              Workflow Visualizer
            </button>
            <button 
              onClick={() => setActiveTab('api')}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'api' ? 'bg-indigo-600/20 border-l-2 border-indigo-500 text-indigo-200' : 'text-slate-400 hover:bg-slate-900 hover:text-white'}`}
            >
              <Database className="h-4 w-4" />
              API Explorer
            </button>
            <button 
              onClick={() => setActiveTab('sdk')}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'sdk' ? 'bg-indigo-600/20 border-l-2 border-indigo-500 text-indigo-200' : 'text-slate-400 hover:bg-slate-900 hover:text-white'}`}
            >
              <Code className="h-4 w-4" />
              SDK Generator
            </button>
          </nav>
        </div>
        
        <div className="p-4 border-t border-slate-800/80">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>Status:</span>
            <span className="flex items-center gap-1.5 font-semibold text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping"></span>
              {isLiveConnection ? "Live API Connected" : "Local Sandbox fallback"}
            </span>
          </div>
        </div>
      </aside>

      {/* Main Panel */}
      <main className="flex-grow flex flex-col overflow-y-auto">
        <header className="h-16 border-b border-slate-800/60 bg-slate-950/20 backdrop-blur-md flex items-center justify-between px-8 shrink-0">
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-400">Current Project:</span>
            <select 
              value={selectedProject?.id || ''} 
              onChange={(e) => setSelectedProject(projects.find(p => p.id === e.target.value))}
              className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1 text-sm focus:outline-none focus:border-indigo-500"
            >
              {projects.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          
          <button 
            onClick={triggerCrawl}
            disabled={crawlingStatus === 'running'}
            className="flex items-center gap-2 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold text-sm px-4 py-2 rounded-lg transition duration-200 shadow-md shadow-indigo-900/40 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="h-4 w-4" />
            Analyze Website
          </button>
        </header>

        <div className="p-8 max-w-6xl mx-auto w-full flex-grow">
          {/* TAB 1: PROJECTS */}
          {activeTab === 'projects' && (
            <div className="space-y-8">
              <div>
                <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2">
                  <Layers className="text-blue-400" />
                  Projects Management
                </h2>
                <p className="text-slate-400 text-sm mt-1">Create projects and track high level statistics.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-6 backdrop-blur-md">
                  <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Discovered Actions</div>
                  <div className="text-3xl font-extrabold mt-2 text-blue-400">{actions.length}</div>
                  <p className="text-xs text-slate-500 mt-1">High level semantic capabilities</p>
                </div>
                <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-6 backdrop-blur-md">
                  <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Mapped API Routes</div>
                  <div className="text-3xl font-extrabold mt-2 text-indigo-400">{apis.length}</div>
                  <p className="text-xs text-slate-500 mt-1">Optimized endpoints mapping</p>
                </div>
                <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-6 backdrop-blur-md">
                  <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Specification Health</div>
                  <div className="text-3xl font-extrabold mt-2 text-emerald-400">98%</div>
                  <p className="text-xs text-slate-500 mt-1">Confidence rating based on selectors</p>
                </div>
              </div>

              {/* Add New Project */}
              <div className="bg-slate-900/30 border border-slate-800/80 rounded-2xl p-8 max-w-xl">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Plus className="text-indigo-400" />
                  Add New Website Project
                </h3>
                <form onSubmit={handleCreateProject} className="space-y-4">
                  <div>
                    <label className="block text-xs text-slate-400 font-semibold mb-1">Project Name</label>
                    <input 
                      type="text" 
                      value={newProjName}
                      onChange={(e) => setNewProjName(e.target.value)}
                      placeholder="My Store Website"
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 font-semibold mb-1">Root URL</label>
                    <input 
                      type="url" 
                      value={newProjUrl}
                      onChange={(e) => setNewProjUrl(e.target.value)}
                      placeholder="http://localhost:8001"
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500 text-sm"
                    />
                  </div>
                  <button 
                    type="submit"
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 rounded-lg transition duration-200 text-sm"
                  >
                    Create Project
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* TAB 2: CRAWL PROGRESS */}
          {activeTab === 'crawl' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2">
                  <Loader2 className={`text-indigo-400 ${crawlingStatus === 'running' ? 'animate-spin' : ''}`} />
                  Crawl & Elements Discovery
                </h2>
                <p className="text-slate-400 text-sm mt-1">Real-time scanner log feed and discovery progress.</p>
              </div>

              {/* Status Header */}
              <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-6 flex justify-between items-center">
                <div>
                  <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Crawl Status</div>
                  <div className="text-lg font-bold capitalize mt-1 flex items-center gap-2">
                    {crawlingStatus === 'running' && <span className="h-2 w-2 rounded-full bg-blue-400 animate-ping"></span>}
                    {crawlingStatus === 'completed' && <CheckCircle className="h-5 w-5 text-emerald-400" />}
                    {crawlingStatus.toUpperCase()}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Page Grouping</div>
                  <div className="text-sm font-semibold mt-1">Consolidating path variables to routes...</div>
                </div>
              </div>

              {/* Console log box */}
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 font-mono text-sm space-y-2 h-96 overflow-y-auto shadow-inner">
                {crawlLogs.map((log, i) => (
                  <div key={i} className="text-slate-300">
                    <span className="text-slate-600 mr-2">[{new Date().toLocaleTimeString()}]</span>
                    {log}
                  </div>
                ))}
                {crawlingStatus === 'running' && (
                  <div className="text-indigo-400 flex items-center gap-2 italic animate-pulse mt-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Crawl running... Scanning forms and interactive links...
                  </div>
                )}
                {crawlLogs.length === 0 && (
                  <div className="text-slate-500 italic text-center py-24">No logs available. Click 'Analyze Website' to initiate analysis.</div>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: ACTIONS */}
          {activeTab === 'actions' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2">
                  <Compass className="text-emerald-400" />
                  Semantic Actions Explorer
                </h2>
                <p className="text-slate-400 text-sm mt-1">Interactive DOM elements classified into high-level agent intents.</p>
              </div>

              <div className="space-y-4">
                {actions.map((act) => {
                  const params = JSON.parse(act.parameters || "[]");
                  return (
                    <div key={act.id} className="bg-slate-900/40 border border-slate-800/80 hover:border-slate-700/80 rounded-xl p-6 transition duration-200">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="flex items-center gap-3">
                            <h3 className="text-lg font-bold text-slate-100">{act.name}</h3>
                            <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase tracking-wider ${act.action_type === 'api' ? 'bg-indigo-600/30 text-indigo-300' : 'bg-slate-800 text-slate-400'}`}>
                              {act.action_type}
                            </span>
                            <span className="text-xs text-slate-500">Confidence Score: <strong className="text-emerald-400">{(act.confidence_score * 100).toFixed(0)}%</strong></span>
                          </div>
                          <p className="text-slate-400 text-sm mt-2">{act.description}</p>
                        </div>
                      </div>

                      <div className="mt-4 pt-4 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <div className="text-xs text-slate-500 font-semibold mb-1 uppercase tracking-wider">DOM Anchor Selector</div>
                          <code className="bg-slate-950 px-2.5 py-1 rounded text-xs border border-slate-850 font-mono text-emerald-400">{act.selector}</code>
                        </div>
                        <div>
                          <div className="text-xs text-slate-500 font-semibold mb-1 uppercase tracking-wider">Parameters Schema</div>
                          {params.length > 0 ? (
                            <div className="space-y-1 mt-1">
                              {params.map((p: any, idx: number) => (
                                <div key={idx} className="text-xs flex items-center gap-2">
                                  <strong className="text-slate-300">{p.name}</strong>
                                  <span className="text-slate-600">({p.type})</span>
                                  {p.selector && <code className="bg-slate-950 text-slate-400 px-1 py-0.5 rounded font-mono scale-95">{p.selector}</code>}
                                </div>
                              ))}
                            </div>
                          ) : (
                            <span className="text-xs text-slate-500 italic">No parameters required</span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 4: WORKFLOW VISUALIZER */}
          {activeTab === 'workflow' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2">
                  <Workflow className="text-blue-400" />
                  Workflow Visualizer
                </h2>
                <p className="text-slate-400 text-sm mt-1">Finite state machines modeling sequential actions.</p>
              </div>

              {workflows.map((wf) => (
                <div key={wf.id} className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-8">
                  <h3 className="text-lg font-bold mb-1">{wf.name}</h3>
                  <p className="text-slate-400 text-sm mb-8">{wf.description}</p>
                  
                  {/* FSM Visualization Flowchart */}
                  <div className="flex flex-col md:flex-row items-center justify-between gap-6 relative">
                    {wf.steps.map((step: any, index: number) => (
                      <React.Fragment key={index}>
                        <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 w-full md:w-56 text-center relative z-10 hover:border-indigo-500 transition duration-300">
                          <div className="text-xs text-indigo-400 font-semibold uppercase tracking-wider">Step {index + 1}</div>
                          <div className="font-bold text-slate-200 mt-2 text-sm">{step.action}</div>
                          <div className="text-xs text-slate-500 mt-2 flex justify-between border-t border-slate-900 pt-2">
                            <span>{step.source_page}</span>
                            <ChevronRight className="h-3.5 w-3.5 text-slate-600" />
                            <span>{step.target_page}</span>
                          </div>
                        </div>
                        {index < wf.steps.length - 1 && (
                          <div className="hidden md:block flex-grow h-0.5 bg-gradient-to-r from-indigo-500 to-blue-500 relative">
                            <span className="absolute right-0 -top-1.5 h-3.5 w-3.5 rounded-full bg-blue-500 animate-ping"></span>
                          </div>
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 5: API EXPLORER */}
          {activeTab === 'api' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2">
                  <Database className="text-indigo-400" />
                  Discovered API Router
                </h2>
                <p className="text-slate-400 text-sm mt-1">Automatic mapping of browser interface events to direct backend API endpoints.</p>
              </div>

              <div className="space-y-4">
                {apis.map((api) => (
                  <div key={api.id} className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-6 flex justify-between items-center hover:border-slate-700 transition">
                    <div>
                      <div className="flex items-center gap-3">
                        <span className="bg-emerald-600/30 text-emerald-300 font-bold px-2.5 py-1 rounded text-xs">
                          {api.method}
                        </span>
                        <code className="text-sm font-mono text-slate-200">{api.url}</code>
                      </div>
                      <div className="text-xs text-slate-500 mt-3">
                        Maps to action intent: <strong className="text-indigo-400">{api.mapped_action}</strong>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-xs text-slate-500 uppercase font-semibold">Request Body Schema</div>
                      <pre className="bg-slate-950 p-2.5 border border-slate-900 rounded font-mono text-xs text-left text-slate-400 mt-1.5">
                        {JSON.stringify(api.request_body, null, 2)}
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 6: SDK GENERATOR */}
          {activeTab === 'sdk' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2">
                    <Code className="text-blue-400" />
                    SDK Code Generator
                  </h2>
                  <p className="text-slate-400 text-sm mt-1">Download compiled agent navigation specs and multi-language wrappers.</p>
                </div>
                <div className="flex gap-3">
                  <a 
                    href="file:///Users/adityadixit/Documents/Code/Preflight Designer/shared/specs/preflight.yaml"
                    download="preflight.yaml"
                    className="flex items-center gap-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg px-3 py-1.5 text-xs font-semibold text-slate-300 transition"
                  >
                    <Download className="h-3.5 w-3.5" />
                    YAML Spec
                  </a>
                  <a 
                    href="file:///Users/adityadixit/Documents/Code/Preflight Designer/shared/specs/sdk.py"
                    download="sdk.py"
                    className="flex items-center gap-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg px-3 py-1.5 text-xs font-semibold text-slate-300 transition"
                  >
                    <Download className="h-3.5 w-3.5" />
                    Python SDK
                  </a>
                </div>
              </div>

              {/* Code Previews */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-3">
                  <div className="text-sm font-bold text-slate-300 flex items-center gap-1.5">
                    <FileText className="h-4 w-4 text-emerald-400" />
                    preflight.yaml (Nav Specification)
                  </div>
                  <pre className="bg-slate-950 border border-slate-800/80 rounded-xl p-5 overflow-auto text-xs font-mono h-96 text-slate-300 shadow-inner">
                    {specs.yaml}
                  </pre>
                </div>

                <div className="space-y-3">
                  <div className="text-sm font-bold text-slate-300 flex items-center gap-1.5">
                    <Code className="h-4 w-4 text-indigo-400" />
                    sdk.py (Python SDK Wrapper)
                  </div>
                  <pre className="bg-slate-950 border border-slate-800/80 rounded-xl p-5 overflow-auto text-xs font-mono h-96 text-slate-300 shadow-inner">
                    {specs.python}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
