import json
from sqlalchemy.orm import Session
from ..models.db_models import Action, Workflow

class WorkflowDiscoveryService:
    def __init__(self, db: Session, project_id: str):
        self.db = db
        self.project_id = project_id

    def discover_and_save(self) -> list:
        # Load all semantic actions for the project
        actions = self.db.query(Action).filter(Action.project_id == self.project_id).all()
        
        # We search for known action combinations to identify workflows
        # E.g. If we have login, search, add_to_cart, and checkout actions, we construct a Purchase Workflow FSM
        workflow_steps = []
        action_names = [a.name for a in actions]

        # Order actions logically: login -> search -> add_to_cart -> checkout
        ordered_flows = []
        if "login" in action_names:
            login_act = next(a for a in actions if a.name == "login")
            ordered_flows.append({
                "action": "login",
                "action_id": login_act.id,
                "description": "Authenticate user session",
                "source_page": "/login",
                "target_page": "/catalog"
            })
            
        if "search_products" in action_names:
            search_act = next(a for a in actions if a.name == "search_products")
            ordered_flows.append({
                "action": "search_products",
                "action_id": search_act.id,
                "description": "Query catalog items",
                "source_page": "/catalog",
                "target_page": "/catalog"
            })
            
        if "add_to_cart" in action_names:
            add_act = next(a for a in actions if a.name == "add_to_cart")
            ordered_flows.append({
                "action": "add_to_cart",
                "action_id": add_act.id,
                "description": "Add product to session cart",
                "source_page": "/product/{id}",
                "target_page": "/checkout"
            })
            
        if "checkout" in action_names:
            check_act = next(a for a in actions if a.name == "checkout")
            ordered_flows.append({
                "action": "checkout",
                "action_id": check_act.id,
                "description": "Finalize order transaction",
                "source_page": "/checkout",
                "target_page": "/catalog"
            })

        workflows_created = []
        if ordered_flows:
            # Check if workflow already exists
            existing = self.db.query(Workflow).filter(
                Workflow.project_id == self.project_id,
                Workflow.name == "purchase_flow"
            ).first()
            
            steps_json = json.dumps(ordered_flows)
            
            if existing:
                existing.steps = steps_json
                workflows_created.append(existing)
            else:
                wf = Workflow(
                    project_id=self.project_id,
                    name="purchase_flow",
                    description="End-to-end purchasing workflow from login to order confirmation",
                    steps=steps_json
                )
                self.db.add(wf)
                workflows_created.append(wf)
                
            self.db.commit()
            print(f"[Workflow Discovery] Constructed finite state machine workflow 'purchase_flow' with {len(ordered_flows)} states.")

        return workflows_created
