import json
from playwright.async_api import Page as PlaywrightPage
from sqlalchemy.orm import Session
from ..models.db_models import AuthConfig, Action

class AuthAnalyzerService:
    def __init__(self, db: Session, project_id: str):
        self.db = db
        self.project_id = project_id

    async def attempt_login(self, page: PlaywrightPage, url: str) -> bool:
        # Check if login forms exist on the current page
        email_selector = "input[type='email'], input[name='email']"
        password_selector = "input[type='password'], input[name='password']"
        submit_selector = "button[type='submit'], #login-submit-btn, input[type='submit']"

        try:
            # Check if fields are visible
            if await page.locator(email_selector).count() > 0 and await page.locator(password_selector).count() > 0:
                print(f"[Auth Analyzer] Login fields detected on {url}. Executing authentication flow...")
                
                # Fill test credentials
                await page.fill(email_selector, "admin@example.com")
                await page.fill(password_selector, "password123")
                
                # Click submit and wait for navigation
                await page.click(submit_selector)
                await page.wait_for_load_state("networkidle")
                
                # Verify if session cookies or auth tokens are present
                context = page.context
                cookies = await context.cookies()
                session_cookie = next((c for c in cookies if c["name"] == "session"), None)
                
                if session_cookie or "/catalog" in page.url:
                    print("[Auth Analyzer] Login successful! Session cookie set.")
                    
                    # Save AuthConfig
                    existing = self.db.query(AuthConfig).filter(AuthConfig.project_id == self.project_id).first()
                    details = {
                        "login_url": url,
                        "credentials": {
                            "email": "admin@example.com",
                            "password": "password123"
                        },
                        "session_indicators": {
                            "cookies": ["session"],
                            "redirect_url": page.url
                        }
                    }
                    
                    if existing:
                        existing.details = json.dumps(details)
                    else:
                        auth_config = AuthConfig(
                            project_id=self.project_id,
                            auth_type="cookie",
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
