import json
from bs4 import BeautifulSoup
from playwright.async_api import Page as PlaywrightPage
from sqlalchemy.orm import Session
from ..models.db_models import Element

class DOMAnalyzerService:
    def __init__(self, db: Session, page_id: str):
        self.db = db
        self.page_id = page_id

    async def analyze(self, page: PlaywrightPage) -> list:
        # Extract interactive elements using Playwright selector queries
        elements_data = []

        # Find buttons
        buttons = await page.locator("button, input[type='submit'], a.btn, a.button").all()
        for btn in buttons:
            try:
                tag = await btn.evaluate("el => el.tagName.toLowerCase()")
                text = await btn.inner_text()
                text = text.strip() if text else ""
                
                # Selector generation
                selector = await self.generate_selector(btn)
                
                # Attributes extraction
                attrs = await btn.evaluate("el => { const out = {}; for (let attr of el.attributes) { out[attr.name] = attr.value; } return out; }")
                
                elements_data.append({
                    "tag_name": tag,
                    "selector": selector,
                    "text_content": text,
                    "element_type": "button",
                    "attributes": attrs,
                    "outer_html": await btn.evaluate("el => el.outerHTML")
                })
            except Exception as e:
                print(f"Error analyzing button: {e}")

        # Find inputs
        inputs = await page.locator("input, textarea, select").all()
        for inp in inputs:
            try:
                tag = await inp.evaluate("el => el.tagName.toLowerCase()")
                inp_type = await inp.get_attribute("type") or "text"
                
                if inp_type in ["submit", "button", "hidden"]:
                    # Skip buttons already captured or hidden fields
                    continue
                    
                placeholder = await inp.get_attribute("placeholder") or ""
                name = await inp.get_attribute("name") or ""
                selector = await self.generate_selector(inp)
                attrs = await inp.evaluate("el => { const out = {}; for (let attr of el.attributes) { out[attr.name] = attr.value; } return out; }")
                
                elements_data.append({
                    "tag_name": tag,
                    "selector": selector,
                    "text_content": placeholder or name,
                    "element_type": "input",
                    "attributes": attrs,
                    "outer_html": await inp.evaluate("el => el.outerHTML")
                })
            except Exception as e:
                print(f"Error analyzing input: {e}")

        # Find forms
        forms = await page.locator("form").all()
        for form in forms:
            try:
                selector = await self.generate_selector(form)
                attrs = await form.evaluate("el => { const out = {}; for (let attr of el.attributes) { out[attr.name] = attr.value; } return out; }")
                elements_data.append({
                    "tag_name": "form",
                    "selector": selector,
                    "text_content": await form.get_attribute("id") or "form",
                    "element_type": "form",
                    "attributes": attrs,
                    "outer_html": await form.evaluate("el => el.outerHTML")
                })
            except Exception as e:
                print(f"Error analyzing form: {e}")

        # Save to DB
        db_elements = []
        for el in elements_data:
            db_el = Element(
                page_id=self.page_id,
                tag_name=el["tag_name"],
                selector=el["selector"],
                text_content=el["text_content"],
                element_type=el["element_type"],
                attributes=json.dumps(el["attributes"]),
                outer_html=el["outer_html"]
            )
            self.db.add(db_el)
            db_elements.append(db_el)
            
        self.db.commit()
        return db_elements

    async def generate_selector(self, element) -> str:
        # Generate robust selectors: prioritizes data-testid, id, name, class, tag
        testid = await element.get_attribute("data-testid")
        if testid:
            return f"[data-testid='{testid}']"

        el_id = await element.get_attribute("id")
        if el_id:
            return f"#{el_id}"

        name = await element.get_attribute("name")
        tag = await element.evaluate("el => el.tagName.toLowerCase()")
        if name:
            return f"{tag}[name='{name}']"

        # Tag + Class fallback
        classes = await element.get_attribute("class")
        if classes:
            class_list = classes.split()
            # use the first 2 classes
            valid_classes = [c for c in class_list if ":" not in c and "[" not in c]  # avoid complex tailwind classes
            if valid_classes:
                return f"{tag}.{'.'.join(valid_classes[:2])}"

        # Full CSS path fallback
        return await element.evaluate("""el => {
            let path = [];
            while (el && el.nodeType === Node.ELEMENT_NODE) {
                let selector = el.nodeName.toLowerCase();
                let sib = el, sibCount = 0, sibIndex = 0;
                while (sib = sib.previousSibling) {
                    if (sib.nodeType === Node.ELEMENT_NODE && sib.nodeName.toLowerCase() === selector) {
                        sibCount++;
                    }
                }
                sib = el;
                while (sib = sib.nextSibling) {
                    if (sib.nodeType === Node.ELEMENT_NODE && sib.nodeName.toLowerCase() === selector) {
                        sibCount++;
                    }
                }
                if (sibCount > 0) {
                    // Find index among siblings of same tag
                    let index = 1;
                    let runner = el;
                    while (runner = runner.previousElementSibling) {
                        if (runner.nodeName.toLowerCase() === selector) {
                            index++;
                        }
                    }
                    selector += `:nth-of-type(${index})`;
                }
                path.unshift(selector);
                el = el.parentNode;
            }
            return path.join(' > ');
        }""")
