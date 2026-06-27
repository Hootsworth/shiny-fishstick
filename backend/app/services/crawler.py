import os
import json
import re
from typing import List, Set
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from sqlalchemy.orm import Session

from ..core.security import decrypt_data
from ..models.db_models import Crawl, Page
from .analyzer import DOMAnalyzerService
from .api_disco import APIDiscoveryService
from .auth import AuthAnalyzerService
from .intent import SemanticIntentService


class CrawlerService:
    def __init__(self, db: Session, project_id: str, crawl_id: str, root_url: str):
        self.db = db
        self.project_id = project_id
        self.crawl_id = crawl_id
        self.root_url = root_url
        self.parsed_root = urlparse(root_url)
        self.visited_urls: Set[str] = set()
        self.pages_to_visit: List[str] = [root_url]
        self.max_pages = 15
        self.max_depth = 3

    def is_same_domain(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.netloc == self.parsed_root.netloc

    def normalize_path(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path
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

    async def crawl(self):
        crawl_obj = self.db.query(Crawl).filter(Crawl.id == self.crawl_id).first()
        if crawl_obj:
            crawl_obj.status = "running"
            self.db.commit()

        try:
            # Check for proxy configuration
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

                # Load saved AuthConfig if exists to restore session
                from ..models.db_models import AuthConfig
                auth_cfg = self.db.query(AuthConfig).filter(AuthConfig.project_id == self.project_id).first()
                if auth_cfg:
                    try:
                        try:
                            details = json.loads(decrypt_data(auth_cfg.details))
                        except Exception:
                            # Fallback if saved as plain text previously
                            details = json.loads(auth_cfg.details)
                        session_ind = details.get("session_indicators", {})

                        # Restore cookies
                        cookies = session_ind.get("cookies", [])
                        if cookies:
                            await context.add_cookies(cookies)
                            print("[Crawler] Restored cookies from saved session config.")

                        # Restore localStorage and sessionStorage
                        # Storage must be added after navigating to the root domain.
                        await page.goto(self.root_url)
                        ls = session_ind.get("localStorage", {})
                        ss = session_ind.get("sessionStorage", {})

                        if ls:
                            await page.evaluate("ls => { for (let k in ls) { localStorage.setItem(k, ls[k]); } }", ls)
                            print("[Crawler] Restored localStorage context.")
                        if ss:
                            await page.evaluate("ss => { for (let k in ss) { sessionStorage.setItem(k, ss[k]); } }", ss)
                            print("[Crawler] Restored sessionStorage context.")

                    except Exception as e:
                        print(f"[Crawler] Error restoring session on startup: {e}")

                # Attach API discovery network sniffer
                api_disco = APIDiscoveryService(self.project_id)
                api_disco.attach(page)

                all_discovered_elements = []

                while self.pages_to_visit and len(self.visited_urls) < self.max_pages:
                    current_url = self.pages_to_visit.pop(0)
                    current_base = current_url.split("?")[0].split("#")[0]
                    if current_base in self.visited_urls:
                        continue

                    print(f"[Crawler] Attempting to visit: {current_url}")

                    try:
                        # Visit page
                        await page.goto(current_url, wait_until="networkidle")

                        actual_url = page.url
                        actual_base = actual_url.split("?")[0].split("#")[0]

                        # Handle authentication redirects dynamically
                        if actual_base != current_base:
                            print(f"[Crawler] Redirected from {current_base} to {actual_base}")
                            if actual_base not in self.visited_urls:
                                self.visited_urls.add(actual_base)
                                # Re-queue the original URL so we visit it later (e.g. after logging in)
                                if current_url not in self.pages_to_visit:
                                    self.pages_to_visit.append(current_url)
                            else:
                                # Destination is already visited, meaning this redirect is fully resolved
                                self.visited_urls.add(current_base)
                            target_url_for_db = actual_url
                            target_base_for_db = actual_base
                        else:
                            self.visited_urls.add(current_base)
                            target_url_for_db = current_url
                            target_base_for_db = current_base

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

                        # DOM Analysis: parse interactive nodes
                        analyzer = DOMAnalyzerService(self.db, db_page.id)
                        elements = await analyzer.analyze(page)
                        all_discovered_elements.extend(elements)

                        # If product detail page, click the add-to-cart button to trigger API discovery
                        if "/product/" in target_url_for_db:
                            add_to_cart_selector = "#add-to-cart-btn"
                            if await page.locator(add_to_cart_selector).count() > 0:
                                print(f"[Crawler] Clicking {add_to_cart_selector} on {target_url_for_db} to capture background API calls...")

                                # Gather context inputs (attributes of the button + URL segments)
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

                        # Check for authentication pages
                        if "/login" in target_url_for_db:
                            auth_service = AuthAnalyzerService(self.db, self.project_id)
                            logged_in = await auth_service.attempt_login(page, target_url_for_db, api_disco)
                            if logged_in:
                                # Queue authenticated routes
                                catalog_url = urljoin(target_url_for_db, "/catalog")
                                catalog_base = catalog_url.split("?")[0].split("#")[0]
                                if catalog_base in self.visited_urls:
                                    self.visited_urls.remove(catalog_base) # allow re-crawling now that we're authed
                                if catalog_url not in self.pages_to_visit:
                                    self.pages_to_visit.append(catalog_url)

                        # Follow links to other pages
                        locator = page.locator("a")
                        count = await locator.count()
                        for i in range(count):
                            href = await locator.nth(i).get_attribute("href")
                            if href:
                                full_url = urljoin(target_url_for_db, href)
                                base_url = full_url.split("?")[0].split("#")[0]
                                if self.is_same_domain(base_url) and base_url not in self.visited_urls:
                                    if "/logout" not in base_url and base_url not in self.pages_to_visit:
                                        self.pages_to_visit.append(base_url)

                        # If product list is found, let's explore one product page to discover add_to_cart action
                        if "/catalog" in target_url_for_db:
                            details_link_selector = "a.view-details-link"
                            if await page.locator(details_link_selector).count() > 0:
                                first_details_href = await page.locator(details_link_selector).first.get_attribute("href")
                                if first_details_href:
                                    product_url = urljoin(target_url_for_db, first_details_href)
                                    product_base = product_url.split("?")[0].split("#")[0]
                                    if product_base not in self.visited_urls and product_url not in self.pages_to_visit:
                                        self.pages_to_visit.append(product_url)

                    except Exception as e:
                        print(f"[Crawler] Error visiting {current_url}: {e}")

                # Run Semantic Intent classification on all extracted elements
                print(f"[Crawler] Crawl completed. Extracting semantic intents for {len(all_discovered_elements)} elements...")
                intent_service = SemanticIntentService(self.db, self.project_id)
                await intent_service.classify_and_save(all_discovered_elements)

                # Save captured API and map actions
                await api_disco.save_discovered_apis(self.db, self.crawl_id)

                await browser.close()

            crawl_obj.status = "completed"
            self.db.commit()
            print("[Crawler] Crawl pipeline successfully finished.")

        except Exception as e:
            print(f"[Crawler] Fatal crawler exception: {e}")
            if crawl_obj:
                crawl_obj.status = "failed"
                crawl_obj.error_message = str(e)
                self.db.commit()
