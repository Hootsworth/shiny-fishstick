import os
import json
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from sqlalchemy.orm import Session
from ..core.config import settings
from ..models.db_models import Action, Element

class SemanticIntentService:
    def __init__(self, db: Session, project_id: str):
        self.db = db
        self.project_id = project_id
        self.api_key = settings.GEMINI_API_KEY
        self.use_llm = bool(self.api_key)
        if self.use_llm:
            try:
                genai.configure(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to configure Gemini SDK: {e}. Falling back to heuristics.")
                self.use_llm = False

    async def classify_and_save(self, elements: List[Element]) -> List[Action]:
        actions = []
        
        # 1. Group inputs under their forms if possible
        # Or look for interactive trigger elements like submit buttons
        forms = [el for el in elements if el.element_type == "form"]
        buttons = [el for el in elements if el.element_type == "button"]
        inputs = [el for el in elements if el.element_type == "input"]

        # Map inputs to their parent forms
        # In our simple mock site, form selectors are:
        # - form#login-form (inputs: email, password, button: continue)
        # - form#search-form (input: q, button: Search)
        # Let's map forms first
        for form in forms:
            action_info = await self.classify_form(form, inputs, buttons)
            if action_info:
                actions.append(action_info)

        # Map independent buttons (like "Add to Cart" button which isn't in a form, but uses JS)
        for btn in buttons:
            # Check if this button is already part of a form's action
            is_form_btn = False
            for form in forms:
                form_attrs = json.loads(form.attributes or "{}")
                form_id = form_attrs.get("id", "")
                if form_id == "login-form" and "login" in btn.selector:
                    is_form_btn = True
                elif form_id == "search-form" and "search" in btn.selector:
                    is_form_btn = True
                elif "checkout-form" in btn.selector:
                    is_form_btn = True
                    
            if not is_form_btn:
                action_info = await self.classify_button(btn)
                if action_info:
                    actions.append(action_info)

        # Deduplicate actions by name in Python first
        unique_actions = {}
        for act in actions:
            unique_actions[act["name"]] = act
        actions = list(unique_actions.values())

        # Save actions to database
        db_actions = []
        for act in actions:
            # Deduplicate parameters by name
            params = act.get("parameters", [])
            deduped_params = []
            seen_params = set()
            for p in params:
                if p["name"] not in seen_params:
                    seen_params.add(p["name"])
                    deduped_params.append(p)
            act["parameters"] = deduped_params

            # Avoid duplicate actions
            existing = self.db.query(Action).filter(
                Action.project_id == self.project_id,
                Action.name == act["name"]
            ).first()
            
            if existing:
                existing.selector = act["selector"]
                existing.parameters = json.dumps(act["parameters"])
                existing.action_type = act["action_type"]
                existing.description = act["description"]
                db_actions.append(existing)
            else:
                db_action = Action(
                    project_id=self.project_id,
                    name=act["name"],
                    description=act["description"],
                    intent=act["intent"],
                    selector=act["selector"],
                    parameters=json.dumps(act["parameters"]),
                    action_type=act["action_type"],
                    confidence_score=act["confidence_score"]
                )
                self.db.add(db_action)
                db_actions.append(db_action)
                
        self.db.commit()
        return db_actions

    async def classify_form(self, form: Element, inputs: List[Element], buttons: List[Element]) -> Optional[Dict[str, Any]]:
        attrs = json.loads(form.attributes or "{}")
        form_id = attrs.get("id", "")
        
        # Determine inputs inside this form
        form_inputs = []
        # simple selector-based matching for mock/generic forms
        if form_id == "login-form":
            form_inputs = [inp for inp in inputs if "email" in inp.selector or "password" in inp.selector]
        elif form_id == "search-form":
            form_inputs = [inp for inp in inputs if "search" in inp.selector or "[name='q']" in inp.selector]
            
        if self.use_llm:
            return await self.classify_form_llm(form, form_inputs)
        else:
            return self.classify_form_heuristics(form_id, form, form_inputs)

    def classify_form_heuristics(self, form_id: str, form: Element, form_inputs: List[Element]) -> Optional[Dict[str, Any]]:
        if form_id == "login-form" or "login" in form.outer_html.lower():
            params = []
            for inp in form_inputs:
                inp_attrs = json.loads(inp.attributes or "{}")
                inp_name = inp_attrs.get("name", "email" if "email" in inp.selector else "password")
                params.append({
                    "name": inp_name,
                    "type": "string",
                    "selector": inp.selector,
                    "required": True
                })
            return {
                "name": "login",
                "description": "Logs in the user with credentials",
                "intent": "login",
                "selector": form.selector,
                "parameters": params,
                "action_type": "browser",
                "confidence_score": 0.95
            }
            
        if form_id == "search-form" or "search" in form.outer_html.lower():
            params = []
            for inp in form_inputs:
                inp_attrs = json.loads(inp.attributes or "{}")
                inp_name = inp_attrs.get("name", "query")
                params.append({
                    "name": inp_name,
                    "type": "string",
                    "selector": inp.selector,
                    "required": True
                })
            return {
                "name": "search_products",
                "description": "Searches for products in the store",
                "intent": "search",
                "selector": form.selector,
                "parameters": params,
                "action_type": "browser",
                "confidence_score": 0.95
            }
            
        return None

    async def classify_button(self, btn: Element) -> Optional[Dict[str, Any]]:
        text = btn.text_content.lower()
        btn_attrs = json.loads(btn.attributes or "{}")
        btn_id = btn_attrs.get("id", "")
        
        if self.use_llm:
            return await self.classify_button_llm(btn)
        else:
            return self.classify_button_heuristics(text, btn_id, btn)

    def classify_button_heuristics(self, text: str, btn_id: str, btn: Element) -> Optional[Dict[str, Any]]:
        if "add to cart" in text or btn_id == "add-to-cart-btn":
            # Product details has a product id parameter in the url usually, or let's read it
            # The button has data-product-id attribute
            attrs = json.loads(btn.attributes or "{}")
            prod_id_attr = attrs.get("data-product-id", "")
            params = []
            if prod_id_attr:
                params.append({
                    "name": "product_id",
                    "type": "string",
                    "selector": btn.selector,
                    "required": True,
                    "attribute_source": "data-product-id"
                })
            return {
                "name": "add_to_cart",
                "description": "Adds the current product to the shopping cart",
                "intent": "add_to_cart",
                "selector": btn.selector,
                "parameters": params,
                "action_type": "browser",
                "confidence_score": 0.95
            }
            
        if "place order" in text or "checkout" in text or btn_id == "checkout-submit-btn":
            return {
                "name": "checkout",
                "description": "Proceeds to place the order and checkout",
                "intent": "checkout",
                "selector": btn.selector,
                "parameters": [],
                "action_type": "browser",
                "confidence_score": 0.90
            }
            
        return None

    # LLM-assisted classifications using Gemini API
    async def classify_form_llm(self, form: Element, form_inputs: List[Element]) -> Optional[Dict[str, Any]]:
        inputs_desc = [{"selector": i.selector, "outer_html": i.outer_html} for i in form_inputs]
        prompt = f"""
        Analyze this web form and its inputs. Classify the semantic intent (e.g. login, search, checkout).
        
        Form HTML:
        {form.outer_html}
        
        Form Inputs:
        {json.dumps(inputs_desc, indent=2)}
        
        Provide the response in raw JSON format matching this schema:
        {{
            "name": "action_name_snake_case",
            "description": "brief user description",
            "intent": "one of: login, search, add_to_cart, checkout, other",
            "selector": "{form.selector}",
            "parameters": [
                {{
                    "name": "parameter_name",
                    "type": "string",
                    "selector": "selector of the input element",
                    "required": true
                }}
            ],
            "action_type": "browser",
            "confidence_score": 0.9
        }}
        
        DO NOT wrap the response in markdown blocks. Return clean JSON.
        """
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = await model.generate_content_async(prompt)
            data = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
            return data
        except Exception as e:
            print(f"Gemini form classification error: {e}. Falling back to heuristics.")
            attrs = json.loads(form.attributes or "{}")
            return self.classify_form_heuristics(attrs.get("id", ""), form, form_inputs)

    async def classify_button_llm(self, btn: Element) -> Optional[Dict[str, Any]]:
        prompt = f"""
        Analyze this button and classify its semantic intent (e.g. add_to_cart, checkout, login).
        
        Button HTML:
        {btn.outer_html}
        
        Provide the response in raw JSON format matching this schema:
        {{
            "name": "action_name_snake_case",
            "description": "brief user description",
            "intent": "one of: add_to_cart, checkout, login, search, other",
            "selector": "{btn.selector}",
            "parameters": [],
            "action_type": "browser",
            "confidence_score": 0.9
        }}
        
        DO NOT wrap the response in markdown blocks. Return clean JSON.
        """
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = await model.generate_content_async(prompt)
            data = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
            return data
        except Exception as e:
            print(f"Gemini button classification error: {e}. Falling back to heuristics.")
            attrs = json.loads(btn.attributes or "{}")
            text = btn.text_content.lower()
            return self.classify_button_heuristics(text, attrs.get("id", ""), btn)
