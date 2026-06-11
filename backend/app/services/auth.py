import json
from playwright.async_api import Page as PlaywrightPage
from sqlalchemy.orm import Session
from ..models.db_models import AuthConfig, Action

class AuthAnalyzerService:
    def __init__(self, db: Session, project_id: str):
        self.db = db
        self.project_id = project_id

    async def attempt_login(self, page: PlaywrightPage, url: str, api_disco=None) -> bool:
        # Generalized selectors
        email_selector = "input[type='email'], input[name='email'], input[name='username'], input[type='text'][name*='user']"
        password_selector = "input[type='password'], input[name='password']"
        submit_selector = "button[type='submit'], #login-submit-btn, input[type='submit'], button:has-text('Sign In'), button:has-text('Login'), button:has-text('Continue')"

        try:
            # Check if fields are visible
            if await page.locator(email_selector).count() > 0 and await page.locator(password_selector).count() > 0:
                print(f"[Auth Analyzer] Login fields detected on {url}. Executing authentication flow...")
                
                # We find the specific visible selectors
                vis_email = None
                vis_pwd = None
                vis_submit = None
                
                for sel in email_selector.split(", "):
                    if await page.locator(sel).count() > 0:
                        vis_email = sel
                        break
                for sel in password_selector.split(", "):
                    if await page.locator(sel).count() > 0:
                        vis_pwd = sel
                        break
                for sel in submit_selector.split(", "):
                    if await page.locator(sel).count() > 0:
                        vis_submit = sel
                        break
                        
                if not vis_email or not vis_pwd:
                    return False
                    
                # Fill test credentials
                await page.fill(vis_email, "admin@example.com")
                await page.fill(vis_pwd, "password123")
                
                if api_disco:
                    api_disco.start_recording("login", {"email": "admin@example.com", "password": "password123"})
                
                # Click submit and wait for navigation
                if vis_submit:
                    await page.click(vis_submit)
                else:
                    # Fallback to keypress
                    await page.press(vis_pwd, "Enter")
                    
                await page.wait_for_load_state("networkidle")
                
                if api_disco:
                    api_disco.stop_recording()
                
                # Verify if session cookies or auth tokens are present
                context = page.context
                cookies = await context.cookies()
                session_cookie = next((c for c in cookies if c["name"] == "session"), None)
                
                # Extract localStorage & sessionStorage
                local_storage = await page.evaluate("() => JSON.stringify(localStorage)")
                session_storage = await page.evaluate("() => JSON.stringify(sessionStorage)")
                
                has_web_storage = False
                ls_dict = {}
                ss_dict = {}
                try:
                    ls_dict = json.loads(local_storage or "{}")
                    ss_dict = json.loads(session_storage or "{}")
                    if ls_dict or ss_dict:
                        has_web_storage = True
                except Exception:
                    pass
                
                if session_cookie or has_web_storage or "/catalog" in page.url:
                    print("[Auth Analyzer] Login successful! Session state captured.")
                    
                    # Save AuthConfig
                    existing = self.db.query(AuthConfig).filter(AuthConfig.project_id == self.project_id).first()
                    details = {
                        "login_url": url,
                        "credentials": {
                            "email": "admin@example.com",
                            "password": "password123"
                        },
                        "session_indicators": {
                            "cookies": cookies,
                            "localStorage": ls_dict,
                            "sessionStorage": ss_dict,
                            "redirect_url": page.url
                        }
                    }
                    
                    if existing:
                        existing.details = json.dumps(details)
                        existing.auth_type = "storage" if has_web_storage else "cookie"
                    else:
                        auth_config = AuthConfig(
                            project_id=self.project_id,
                            auth_type="storage" if has_web_storage else "cookie",
                            details=json.dumps(details)
                        )
                        self.db.add(auth_config)
                    self.db.commit()
                    return True
                else:
                    print("[Auth Analyzer] Login form submitted but session not established.")
        except Exception as e:
            print(f"[Auth Analyzer] Error during auth simulation: {e}")
            
        return False
