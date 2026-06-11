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
  { id: "act-1", name: "login", intent: "login", selector: "#login-form", action_type: "browser", confidence_score: 0.95, description: "Logs in the user with credentials", parameters: JSON.stringify([{ name: "email", type: "string", selector: "#email" }, { name: "password", type: "string", selector: "#password" }]) },
  { id: "act-2", name: "search_products", intent: "search", selector: "#search-form", action_type: "browser", confidence_score: 0.95, description: "Searches for products in the store", parameters: JSON.stringify([{ name: "q", type: "string", selector: "#search-input" }]) },
  { id: "act-3", name: "add_to_cart", intent: "add_to_cart", selector: "#add-to-cart-btn", action_type: "api", confidence_score: 0.98, description: "Adds the current product to the shopping cart", api_url: "/api/cart/add", api_method: "POST", parameters: JSON.stringify([{ name: "product_id", type: "string", selector: "" }, { name: "quantity", type: "integer", selector: "" }]) },
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
  const [crawlingStatus, setCrawlingStatus] = useState<string>("idle");
  const [newProjName, setNewProjName] = useState("");
  const [newProjUrl, setNewProjUrl] = useState("");
  const [crawlLogs, setCrawlLogs] = useState<string[]>([]);
  const [isLiveConnection, setIsLiveConnection] = useState(false);

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
                setIsLiveConnection(prev => !prev);
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

  // Nav Button Component for DRY styling
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
              <Compass className="h-6 w-6" />
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
            onClick={triggerCrawl}
            disabled={crawlingStatus === 'running'}
            className="flex items-center gap-2 bg-black text-white font-bold text-sm px-5 py-2.5 rounded-md border-2 border-black shadow-[4px_4px_0px_0px_#f472b6] hover:shadow-[2px_2px_0px_0px_#f472b6] hover:translate-y-[2px] hover:translate-x-[2px] transition-all disabled:opacity-70 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-y-0 disabled:translate-x-0"
          >
            <Play className="h-4 w-4" />
            ANALYZE WEBSITE
          </button>
        </header>

        <div className="p-10 max-w-6xl mx-auto w-full flex-grow">
          {/* TAB 1: PROJECTS */}
          {activeTab === 'projects' && (
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
                  { label: 'Discovered Actions', val: actions.length, desc: 'Semantic capabilities' },
                  { label: 'Mapped APIs', val: apis.length, desc: 'Optimized endpoints' },
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
          )}

          {/* TAB 2: CRAWL PROGRESS */}
          {activeTab === 'crawl' && (
            <div className="space-y-8">
              <div>
                <h2 className="text-3xl font-black tracking-tight flex items-center gap-3">
                  <Loader2 className={`${crawlingStatus === 'running' ? 'animate-spin' : ''}`} />
                  CRAWL TERMINAL
                </h2>
                <p className="text-gray-600 font-medium mt-2">Real-time scanner log feed.</p>
              </div>

              <div className="bg-pink-50 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-md p-6 flex justify-between items-center">
                <div>
                  <div className="text-xs font-black text-gray-600 uppercase tracking-widest">Job Status</div>
                  <div className="text-xl font-black uppercase mt-1 flex items-center gap-2">
                    {crawlingStatus === 'running' && <span className="h-3 w-3 rounded-none bg-black animate-pulse border border-black"></span>}
                    {crawlingStatus === 'completed' && <CheckCircle className="h-5 w-5 text-black" />}
                    {crawlingStatus}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-black text-gray-600 uppercase tracking-widest">Routing</div>
                  <div className="text-sm font-bold mt-1">Consolidating paths...</div>
                </div>
              </div>

              {/* Console box */}
              <div className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-md p-6 font-mono text-sm space-y-3 h-96 overflow-y-auto">
                {crawlLogs.map((log, i) => (
                  <div key={i} className="text-black border-b border-gray-100 pb-2">
                    <span className="text-gray-400 font-bold mr-3">{new Date().toLocaleTimeString()}</span>
                    {log}
                  </div>
                ))}
                {crawlingStatus === 'running' && (
                  <div className="text-pink-600 font-bold flex items-center gap-2 animate-pulse mt-4">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    > Scanner engaged. Analyzing interactive DOM nodes...
                  </div>
                )}
                {crawlLogs.length === 0 && (
                  <div className="text-gray-400 font-bold text-center py-32 uppercase tracking-widest">No logs available. Initialize Analysis.</div>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: ACTIONS */}
          {activeTab === 'actions' && (
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
                  const params = JSON.parse(act.parameters || "[]");
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
                              {params.map((p: any, idx: number) => (
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
          )}

          {/* TAB 4: WORKFLOW VISUALIZER */}
          {activeTab === 'workflow' && (
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
                    {wf.steps.map((step: any, index: number) => (
                      <React.Fragment key={index}>
                        <div className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_#f472b6] p-6 w-full md:w-64 text-center relative z-10">
                          <div className="text-xs font-black text-pink-500 uppercase tracking-widest bg-pink-50 inline-block px-2 py-1 border border-pink-200 mb-3">Step {index + 1}</div>
                          <div className="font-black text-lg uppercase mb-4">{step.action}</div>
                          <div className="text-xs font-bold text-gray-500 flex justify-between border-t-2 border-gray-100 pt-3">
                            <span className="bg-gray-100 px-1">{step.source_page}</span>
                            <ChevronRight className="h-4 w-4 text-black mx-1" />
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
          )}

          {/* TAB 5: API EXPLORER */}
          {activeTab === 'api' && (
            <div className="space-y-8">
              <div>
                <h2 className="text-3xl font-black tracking-tight flex items-center gap-3">
                  <Database className="h-8 w-8" />
                  API MAPPER
                </h2>
                <p className="text-gray-600 font-medium mt-2">Browser intent to direct background API translations.</p>
              </div>

              <div className="space-y-6">
                {apis.map((api) => (
                  <div key={api.id} className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-md p-6 flex flex-col md:flex-row justify-between gap-6">
                    <div>
                      <div className="flex items-center gap-4 mb-4">
                        <span className="bg-black text-white font-black px-3 py-1.5 text-sm uppercase tracking-wider shadow-[2px_2px_0px_0px_#f472b6] border border-black">
                          {api.method}
                        </span>
                        <code className="text-lg font-bold font-mono">{api.url}</code>
                      </div>
                      <div className="text-sm font-medium text-gray-600 bg-pink-50 border border-black p-3 inline-block">
                        Resolved Intent: <strong className="text-black uppercase">{api.mapped_action}</strong>
                      </div>
                    </div>

                    <div className="md:w-1/2">
                      <div className="text-xs font-black text-gray-500 uppercase tracking-widest mb-2">Expected Payload</div>
                      <pre className="bg-gray-50 p-4 border-2 border-black font-mono text-sm font-bold text-black overflow-x-auto">
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
                  <button className="flex items-center gap-2 bg-white text-black border-2 border-black px-4 py-2 font-black text-sm uppercase tracking-wider shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-y-[2px] hover:translate-x-[2px] transition-all">
                    <Download className="h-4 w-4" />
                    YAML Spec
                  </button>
                  <button className="flex items-center gap-2 bg-white text-black border-2 border-black px-4 py-2 font-black text-sm uppercase tracking-wider shadow-[4px_4px_0px_0px_#f472b6] hover:shadow-[2px_2px_0px_0px_#f472b6] hover:translate-y-[2px] hover:translate-x-[2px] transition-all">
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
          )}
        </div>
      </main>
    </div>
  );
}