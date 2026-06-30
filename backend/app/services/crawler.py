import asyncio
import json
import os
import re
from collections import deque
from datetime import datetime, timezone
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse

import aiohttp
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from sqlalchemy.orm import Session

from ..core.logging import log
from ..core.security import decrypt_data
from ..models.db_models import Crawl, Page
from .analyzer import DOMAnalyzerService
from .api_disco import APIDiscoveryService
from .auth import AuthAnalyzerService
from .intent import SemanticIntentService


class CrawlerService:
    def __init__(self, db: Session, project_id: str, crawl_id: str, root_url: str, agent_id: Optional[str] = None):
        self.db = db
        self.project_id = project_id
        self.crawl_id = crawl_id
        self.root_url = root_url
        self.parsed_root = urlparse(root_url)
        self.visited_urls: Set[str] = set()
        self.pages_to_visit = deque([root_url])
        self.max_pages = 15
        self.max_depth = 3
        self.url_depths: dict[str, int] = {root_url: 0}
        self.agent_id = agent_id
        self.all_discovered_elements = []

    def is_same_domain(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            return parsed.netloc == self.parsed_root.netloc
        except Exception:
            return False

    def normalize_path(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            path = parsed.path
        except Exception:
            path = url
        if not path or path == "/":
            return "/"
        segments = path.strip("/").split("/")
        new_segments = []
        for seg in segments:
            if seg.isdigit():
                new_segments.append("{id}")
            elif re.match(r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$', seg):
                new_segments.append("{id}")
            else:
                new_segments.append(seg)
        return "/" + "/".join(new_segments)

    async def crawl_page(self, page, current_url: str, api_disco: APIDiscoveryService) -> List[str]:
        current_base = current_url.split("?")[0].split("#")[0]
        discovered_links = []
        log.info("crawler_visit", url=current_url)

        try:
            await page.goto(current_url, wait_until="networkidle")

            actual_url = page.url
            actual_base = actual_url.split("?")[0].split("#")[0]

            if actual_base != current_base:
                log.info("crawler_redirect", from_url=current_base, to_url=actual_base)
                if actual_base not in self.visited_urls:
                    self.visited_urls.add(actual_base)
                    discovered_links.append(current_url)
                else:
                    self.visited_urls.add(current_base)
                target_url_for_db = actual_url
            else:
                self.visited_urls.add(current_base)
                target_url_for_db = current_url

            normalized_path = self.normalize_path(target_url_for_db)
            title = await page.title()

            db_page = Page(
                crawl_id=self.crawl_id,
                url=target_url_for_db,
                path=normalized_path,
                title=title
            )
            self.db.add(db_page)
            self.db.commit()
            self.db.refresh(db_page)

            analyzer = DOMAnalyzerService(self.db, db_page.id)
            elements = await analyzer.analyze(page)
            self.all_discovered_elements.extend(elements)

            if "/product/" in target_url_for_db:
                add_to_cart_selector = "#add-to-cart-btn"
                if await page.locator(add_to_cart_selector).count() > 0:
                    log.info("crawler_xhr_probe", selector=add_to_cart_selector, url=target_url_for_db)

                    parsed_url = urlparse(target_url_for_db)
                    path_segs = [s for s in parsed_url.path.split("/") if s]
                    context_inputs = {}
                    for idx, seg in enumerate(path_segs):
                        context_inputs[f"url_seg_{idx}"] = seg
                        if seg.isdigit() or len(seg) > 5:
                            context_inputs["url_id"] = seg

                    try:
                        btn_attrs = await page.locator(add_to_cart_selector).evaluate("el => { const out = {}; for (let attr of el.attributes) { out[attr.name] = attr.value; } return out; }")
                        context_inputs.update(btn_attrs)
                    except Exception:
                        pass

                    api_disco.start_recording("add_to_cart", context_inputs)
                    await page.click(add_to_cart_selector)
                    await page.wait_for_load_state("networkidle")
                    api_disco.stop_recording()

            if "/login" in target_url_for_db:
                auth_service = AuthAnalyzerService(self.db, self.project_id)
                logged_in = await auth_service.attempt_login(page, target_url_for_db, api_disco)
                if logged_in:
                    catalog_url = urljoin(target_url_for_db, "/catalog")
                    catalog_base = catalog_url.split("?")[0].split("#")[0]
                    if catalog_base in self.visited_urls:
                        self.visited_urls.remove(catalog_base)
                    discovered_links.append(catalog_url)

            locator = page.locator("a")
            count = await locator.count()
            for i in range(count):
                href = await locator.nth(i).get_attribute("href")
                if href:
                    full_url = urljoin(target_url_for_db, href)
                    base_url = full_url.split("?")[0].split("#")[0]
                    if self.is_same_domain(base_url) and base_url not in self.visited_urls:
                        if "/logout" not in base_url:
                            discovered_links.append(base_url)

            if "/catalog" in target_url_for_db:
                details_link_selector = "a.view-details-link"
                if await page.locator(details_link_selector).count() > 0:
                    first_details_href = await page.locator(details_link_selector).first.get_attribute("href")
                    if first_details_href:
                        product_url = urljoin(target_url_for_db, first_details_href)
                        product_base = product_url.split("?")[0].split("#")[0]
                        if product_base not in self.visited_urls:
                            discovered_links.append(product_url)

        except Exception as e:
            log.error("crawler_page_error", url=current_url, error=str(e))

        return discovered_links

    async def crawl(self):
        crawl_obj = self.db.query(Crawl).filter(Crawl.id == self.crawl_id).first()
        if crawl_obj:
            crawl_obj.status = "running"
            crawl_obj.started_at = datetime.now(timezone.utc)
            self.db.commit()

        try:
            proxy_server = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
            proxy_config = None
            if proxy_server:
                proxy_config = {"server": proxy_server}
                proxy_user = os.environ.get("PROXY_USER")
                proxy_pass = os.environ.get("PROXY_PASS")
                if proxy_user and proxy_pass:
                    proxy_config["username"] = proxy_user
                    proxy_config["password"] = proxy_pass

            async with Stealth().use_async(async_playwright()) as p:
                browser = await p.chromium.launch(headless=True)

                context_args = {}
                if proxy_config:
                    context_args["proxy"] = proxy_config
                context = await browser.new_context(**context_args)

                page = await context.new_page()

                from ..models.db_models import AuthConfig
                auth_cfg = self.db.query(AuthConfig).filter(AuthConfig.project_id == self.project_id).first()
                if auth_cfg:
                    try:
                        try:
                            details = json.loads(decrypt_data(auth_cfg.details))
                        except Exception:
                            details = json.loads(auth_cfg.details)
                        session_ind = details.get("session_indicators", {})

                        cookies = session_ind.get("cookies", [])
                        if cookies:
                            await context.add_cookies(cookies)
                            log.info("session_cookies_restored")

                        await page.goto(self.root_url)
                        ls = session_ind.get("localStorage", {})
                        ss = session_ind.get("sessionStorage", {})

                        if ls:
                            await page.evaluate("ls => { for (let k in ls) { localStorage.setItem(k, ls[k]); } }", ls)
                            log.info("session_local_storage_restored")
                        if ss:
                            await page.evaluate("ss => { for (let k in ss) { sessionStorage.setItem(k, ss[k]); } }", ss)
                            log.info("session_storage_restored")

                    except Exception as e:
                        log.error("session_restore_failed", error=str(e))

                api_disco = APIDiscoveryService(self.project_id)
                api_disco.attach(page)

                # Route allocation: Agent Clustered mode vs Single Node mode
                if self.agent_id:
                    hub_url = f"ws://localhost:8000/api/ws/hub/{self.agent_id}"
                    log.info("crawler_agent_connecting_hub", url=hub_url)
                    async with aiohttp.ClientSession() as session:
                        async with session.ws_connect(hub_url) as ws:
                            # Register seed URL
                            await ws.send_json({
                                "type": "discover",
                                "urls": [self.root_url]
                            })

                            while len(self.visited_urls) < self.max_pages:
                                await ws.send_json({"type": "request_work"})
                                try:
                                    msg = await asyncio.wait_for(ws.receive_json(), timeout=5.0)
                                except asyncio.TimeoutError:
                                    log.info("crawler_agent_idle_timeout")
                                    break
                                except Exception as e:
                                    log.warning("crawler_agent_ws_receive_error", error=str(e))
                                    break

                                if msg.get("type") == "assign":
                                    current_url = msg["url"]
                                    discovered_links = await self.crawl_page(page, current_url, api_disco)
                                    await ws.send_json({
                                        "type": "discover",
                                        "urls": discovered_links
                                    })
                else:
                    # Single Node Mode — BFS with depth tracking
                    while self.pages_to_visit and len(self.visited_urls) < self.max_pages:
                        current_url = self.pages_to_visit.popleft()
                        current_base = current_url.split("?")[0].split("#")[0]
                        if current_base in self.visited_urls:
                            continue

                        current_depth = self.url_depths.get(current_url, 0)
                        if current_depth > self.max_depth:
                            log.info("crawler_depth_limit", url=current_url, depth=current_depth, max_depth=self.max_depth)
                            continue

                        discovered_links = await self.crawl_page(page, current_url, api_disco)
                        for link in discovered_links:
                            link_base = link.split("?")[0].split("#")[0]
                            if link_base not in self.visited_urls and link not in self.pages_to_visit:
                                self.pages_to_visit.append(link)
                                if link not in self.url_depths:
                                    self.url_depths[link] = current_depth + 1

                log.info("crawler_extraction_complete", count=len(self.all_discovered_elements))
                intent_service = SemanticIntentService(self.db, self.project_id)
                await intent_service.classify_and_save(self.all_discovered_elements)

                await api_disco.save_discovered_apis(self.db, self.crawl_id)
                await browser.close()

            crawl_obj.status = "completed"
            crawl_obj.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            log.info("crawler_pipeline_completed")

        except Exception as e:
            log.error("crawler_fatal_error", error=str(e))
            if crawl_obj:
                crawl_obj.status = "failed"
                crawl_obj.error_message = str(e)
                self.db.commit()
