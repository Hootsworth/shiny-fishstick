export const API_BASE = "http://localhost:8000/api";

export interface Project {
  id: string;
  name: string;
  root_url: string;
  created_at: string;
}

export interface Action {
  id: string;
  name: string;
  intent: string;
  selector: string;
  action_type: string;
  confidence_score: number;
  description: string;
  parameters: string;
  api_url?: string;
  api_method?: string;
}

export interface WorkflowStep {
  action: string;
  source_page: string;
  target_page: string;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
}

export interface ApiRoute {
  id: string;
  method: string;
  url: string;
  request_body: any;
  mapped_action: string;
}

export interface Specs {
  yaml: string;
  python: string;
}

export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/projects`);
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}

export async function createProject(name: string, rootUrl: string): Promise<Project> {
  const res = await fetch(`${API_BASE}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, root_url: rootUrl }),
  });
  if (!res.ok) throw new Error("Failed to create project");
  return res.json();
}

export async function fetchActions(projectId: string): Promise<Action[]> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/actions`);
  if (!res.ok) throw new Error("Failed to fetch actions");
  return res.json();
}

export async function fetchWorkflows(projectId: string): Promise<Workflow[]> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/workflows`);
  if (!res.ok) throw new Error("Failed to fetch workflows");
  return res.json();
}

export async function fetchSpecYaml(projectId: string): Promise<string> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/spec`);
  if (!res.ok) throw new Error("Failed to fetch spec");
  return res.text();
}

export async function fetchPythonSDK(projectId: string): Promise<string> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/sdk/python`);
  if (!res.ok) throw new Error("Failed to fetch python sdk");
  return res.text();
}

export async function triggerCrawl(projectId: string): Promise<{ crawl_id: string }> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/crawl`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to trigger crawl");
  return res.json();
}

export async function fetchCrawlStatus(crawlId: string): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/crawls/${crawlId}`);
  if (!res.ok) throw new Error("Failed to fetch crawl status");
  return res.json();
}
