// Shiny Fishstick Generated TypeScript SDK
import { chromium, Browser, BrowserContext, Page } from 'playwright';

export class ShinyFishstickSiteSDK {
    private rootUrl: string = "http://localhost:8001";
    private browser: Browser | null = null;
    private context: BrowserContext | null = null;
    private page: Page | null = null;

    async start(headless: boolean = true): Promise<ShinyFishstickSiteSDK> {
        this.browser = await chromium.launch({ headless });
        this.context = await this.browser.newContext();
        this.page = await this.context.newPage();
        await this.page.goto(this.rootUrl);
        return this;
    }

    async close(): Promise<void> {
        if (this.browser) await this.browser.close();
    }

    async login(email: string, password: string): Promise<any> {
        
        await this.page.goto(`${this.rootUrl}/login`);
        await this.page.fill("#email", String(email));
        await this.page.fill("#password", String(password));
        await this.page.click("#login-submit-btn");
        await this.page.waitForLoadState("networkidle");
    }

    async search_products(q: string): Promise<any> {
        
        await this.page.goto(`${this.rootUrl}/catalog`);
        await this.page.fill("#search-input", String(q));
        await this.page.click("#search-submit-btn");
        await this.page.waitForLoadState("networkidle");
    }

    async checkout(): Promise<any> {
        
        await this.page.goto(`${this.rootUrl}/checkout`);
        await this.page.click("#checkout-submit-btn");
        await this.page.waitForLoadState("networkidle");
    }

    async add_to_cart(product_id: string, quantity: number): Promise<any> {
        
        const sessionCookie = (await this.context.cookies()).find(c => c.name === 'session');
        const cookieHeader = sessionCookie ? `session=${sessionCookie.value}` : '';
        const response = await fetch(`${this.rootUrl}/api/cart/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cookie': cookieHeader
            },
            body: JSON.stringify({ product_id, quantity })
        });
        return response.json();
    }

}
