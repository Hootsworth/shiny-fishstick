from typing import Dict, List, Set

from fastapi import WebSocket

from ..core.logging import log


class CrawlerAgentHub:
    def __init__(self):
        self.active_agents: Dict[str, WebSocket] = {}
        self.discovered_urls: Set[str] = set()
        self.visited_urls: Set[str] = set()
        self.pending_queue: List[str] = []
        self.assignments: Dict[str, str] = {}  # agent_id -> assigned_url

    async def register(self, agent_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_agents[agent_id] = websocket
        log.info("agent_hub_registered", agent_id=agent_id)

    async def unregister(self, agent_id: str):
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]
        if agent_id in self.assignments:
            unassigned_url = self.assignments[agent_id]
            if unassigned_url not in self.visited_urls:
                self.pending_queue.append(unassigned_url)
            del self.assignments[agent_id]
        log.info("agent_hub_unregistered", agent_id=agent_id)

    async def broadcast_discoveries(self, agent_id: str, urls: List[str]):
        new_discoveries = []
        for url in urls:
            if url not in self.discovered_urls:
                self.discovered_urls.add(url)
                self.pending_queue.append(url)
                new_discoveries.append(url)
        log.info("agent_hub_discoveries", agent_id=agent_id, count=len(new_discoveries))
        await self.dispatch_work()

    async def request_work(self, agent_id: str):
        if agent_id in self.assignments:
            completed_url = self.assignments[agent_id]
            self.visited_urls.add(completed_url)
            del self.assignments[agent_id]
        await self.dispatch_work()

    async def dispatch_work(self):
        for agent_id, ws in list(self.active_agents.items()):
            if agent_id not in self.assignments and self.pending_queue:
                next_url = self.pending_queue.pop(0)
                self.assignments[agent_id] = next_url
                try:
                    await ws.send_json({
                        "type": "assign",
                        "url": next_url
                    })
                    log.info("agent_hub_assigned", agent_id=agent_id, url=next_url)
                except Exception as e:
                    log.warning("agent_hub_send_failed", agent_id=agent_id, error=str(e))
                    self.pending_queue.append(next_url)
                    if agent_id in self.assignments:
                        del self.assignments[agent_id]


agent_hub = CrawlerAgentHub()
