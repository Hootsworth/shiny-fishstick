// Shiny Fishstick Generated TypeScript SDK
import { chromium, Browser, BrowserContext, Page } from 'playwright';

export class ShinyFishstickSiteSDK {
    private rootUrl: string = "http://localhost:8001";
    private browser: Browser | null = null;
    private context: BrowserContext | null = null;
    private page: Page | null = null;
    private sessionCookies: any[] = [];
    private sessionLocalStorage: any = {};
    private sessionSessionStorage: any = {};

    async start(headless: boolean = true, sessionData?: any): Promise<ShinyFishstickSiteSDK> {
        this.browser = await chromium.launch({ headless });
        this.context = await this.browser.newContext();
        this.page = await this.context.newPage();

        if (sessionData) {
            if (sessionData.cookies) {
                await this.context.addCookies(sessionData.cookies);
            }
            await this.page.goto(this.rootUrl);
            if (sessionData.localStorage) {
                await this.page.evaluate((ls) => {
                    for (let k in ls) localStorage.setItem(k, ls[k]);
                }, sessionData.localStorage);
            }
            if (sessionData.sessionStorage) {
                await this.page.evaluate((ss) => {
                    for (let k in ss) sessionStorage.setItem(k, ss[k]);
                }, sessionData.sessionStorage);
            }
            this.sessionCookies = sessionData.cookies || [];
            this.sessionLocalStorage = sessionData.localStorage || {};
            this.sessionSessionStorage = sessionData.sessionStorage || {};
        } else {
            await this.page.goto(this.rootUrl);
            this.sessionCookies = [];
            this.sessionLocalStorage = {};
            this.sessionSessionStorage = {};
        }
        return this;
    }

    async exportSession(): Promise<any> {
        return {
            cookies: this.sessionCookies || [],
            localStorage: this.sessionLocalStorage || {},
            sessionStorage: this.sessionSessionStorage || {}
        };
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
        this.sessionCookies = await this.context.cookies();
        try {
            this.sessionLocalStorage = JSON.parse(await this.page.evaluate(() => JSON.stringify(localStorage)) || '{}');
            this.sessionSessionStorage = JSON.parse(await this.page.evaluate(() => JSON.stringify(sessionStorage)) || '{}');
        } catch (e) {
            this.sessionLocalStorage = {};
            this.sessionSessionStorage = {};
        }
    }

    async search_products(q: string): Promise<any> {
        
        await this.page.goto(`${this.rootUrl}/catalog`);
        await this.page.fill("#search-input", String(q));
        await this.page.click("#search-submit-btn");
        await this.page.waitForLoadState("networkidle");
        this.sessionCookies = await this.context.cookies();
        try {
            this.sessionLocalStorage = JSON.parse(await this.page.evaluate(() => JSON.stringify(localStorage)) || '{}');
            this.sessionSessionStorage = JSON.parse(await this.page.evaluate(() => JSON.stringify(sessionStorage)) || '{}');
        } catch (e) {
            this.sessionLocalStorage = {};
            this.sessionSessionStorage = {};
        }
    }

    async checkout(): Promise<any> {
        
        await this.page.goto(`${this.rootUrl}/checkout`);
        await this.page.click("#checkout-submit-btn");
        await this.page.waitForLoadState("networkidle");
        this.sessionCookies = await this.context.cookies();
        try {
            this.sessionLocalStorage = JSON.parse(await this.page.evaluate(() => JSON.stringify(localStorage)) || '{}');
            this.sessionSessionStorage = JSON.parse(await this.page.evaluate(() => JSON.stringify(sessionStorage)) || '{}');
        } catch (e) {
            this.sessionLocalStorage = {};
            this.sessionSessionStorage = {};
        }
    }

    async add_to_cart(product_id: string, quantity: number): Promise<any> {
        
        const sessionCookie = this.sessionCookies.find(c => c.name === 'session');
        const cookieHeader = sessionCookie ? `session=${sessionCookie.value}` : '';
        const response = await fetch(`${this.rootUrl}/api/cart/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cookie': cookieHeader
            },
            body: JSON.stringify({ "product_id": product_id, "quantity": quantity }),
        });
        return response.json();
    }

}
