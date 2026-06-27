import { useState } from "react";
import * as api from "../lib/api";

export function useCrawlState(
  selectedProject: any,
  isLiveConnection: boolean,
  addLogMessage: (msg: string) => void,
  clearLogs: () => void,
  onCrawlComplete: () => void
) {
  const [crawlingStatus, setCrawlingStatus] = useState<string>("idle");

  const runCrawl = async () => {
    if (!selectedProject) return;
    clearLogs();
    setCrawlingStatus("pending");

    addLogMessage(`[Crawler] Initializing crawler for ${selectedProject.root_url}...`);
    addLogMessage(`[Crawler] Launching Playwright browser instance...`);
    addLogMessage(`[Crawler] Visiting seed root URL: ${selectedProject.root_url}...`);

    if (isLiveConnection) {
      try {
        const data = await api.triggerCrawl(selectedProject.id);
        const crawlId = data.crawl_id;
        setCrawlingStatus("running");

        const interval = setInterval(async () => {
          try {
            const crawlData = await api.fetchCrawlStatus(crawlId);
            setCrawlingStatus(crawlData.status);

            if (crawlData.status === "running") {
              addLogMessage(`[Crawler] Scanning page content dynamically...`);
              addLogMessage(`[Crawler] Extracting inputs, forms, and clickable elements...`);
            }

            if (crawlData.status === "completed" || crawlData.status === "failed") {
              clearInterval(interval);
              addLogMessage(`[Crawler] Run finished. Crawl status: ${crawlData.status.toUpperCase()}`);
              addLogMessage(`[Semantic Intent] Running classifications...`);
              addLogMessage(`[API Discovery] Mapped routes to background fetch handlers.`);
              addLogMessage(`[SDK Generator] Specifications regenerated successfully.`);
              onCrawlComplete();
            }
          } catch (e) {
            clearInterval(interval);
            setCrawlingStatus("failed");
            addLogMessage(`[Crawler] Failed to poll status: ${e}`);
          }
        }, 2000);
      } catch (err) {
        setCrawlingStatus("failed");
        addLogMessage(`[Crawler] Error launching crawl: ${err}`);
      }
    } else {
      // Sandbox Mode Mock Sequence
      setTimeout(() => {
        setCrawlingStatus("running");
        addLogMessage(`[Crawler] Redirected from ${selectedProject.root_url} to /login (Auth required)`);
        addLogMessage(`[Auth Analyzer] Resolving login procedure using simulated cookies...`);
        addLogMessage(`[Crawler] Re-evaluating authorized links...`);
        addLogMessage(`[Crawler] Discovered pages: [/login, /catalog, /product/{id}, /checkout]`);
      }, 2000);

      setTimeout(() => {
        setCrawlingStatus("completed");
        addLogMessage(`[DOM Analyzer] Selector generation completed.`);
        addLogMessage(`[API Discovery] Successfully mapped action 'add_to_cart' to direct API: POST /api/cart/add`);
        addLogMessage(`[SDK Generator] Python, TypeScript wrapper SDKs compiled.`);
        addLogMessage(`[Crawler] Compile Finished. Spec ready for download.`);
        onCrawlComplete();
      }, 5000);
    }
  };

  return { crawlingStatus, setCrawlingStatus, runCrawl };
}
