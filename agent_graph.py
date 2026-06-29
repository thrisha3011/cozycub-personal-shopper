from typing import TypedDict, List, Dict, Any, Optional
import json
import re
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from search_engine import get_live_jiomart_item

# 1. Define Global State Schema Dictionary
class AgentState(TypedDict):
    user_message: str
    chat_history: List[Dict[str, str]]
    next_action: str  # 'CHAT', 'SEARCH', 'INVOICE_READY', 'COMPLETE'
    items_list: List[Dict[str, Any]]
    max_budget: Optional[float]
    current_total: float
    agent_reply: str

# Connect to Hosted Groq cloud cluster node using your developer API Key
# (Replace this string with your real Groq API key token!)
GROQ_API_KEY = "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"
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama3-8b-8192", temperature=0.1)

# --- Node A: Conversation & Planner Agent ---
def planner_node(state: AgentState) -> Dict[str, Any]:
    print("[Agent Node] Planner & Router Agent active...")
    user_input = state["user_message"]
    
    prompt = (
        f"You are CozyCub, a smart personal shooper agent. Analyze the user request: '{user_input}'.\n"
        "Determine if they want to buy items or are just talking. Respond ONLY with a raw JSON object matching this structure:\n"
        "{\n"
        "  \"is_shopping\": true or false,\n"
        "  \"budget\": number or null,\n"
        "  \"extracted_items\": [{\"product\": \"item name\", \"qty\": \"quantity string\", \"status\": \"PENDING\"}],\n"
        "  \"reply\": \"ChatGPT style natural response\"\n"
        "}"
    )
    
    try:
        res = llm.invoke(prompt)
        data = json.loads(re.sub(r"```json|```", "", res.content).strip())
        
        if data.get("is_shopping"):
            return {
                "next_action": "SEARCH",
                "items_list": data.get("extracted_items", []),
                "max_budget": data.get("budget"),
                "agent_reply": data.get("reply", "")
            }
        else:
            return {"next_action": "CHAT", "agent_reply": data.get("reply", ""), "items_list": []}
    except Exception:
        return {"next_action": "CHAT", "agent_reply": "I'm here! What groceries can I find on JioMart today?", "items_list": []}

# --- Node B: Shopping Tool Execution Agent ---
def shopping_node(state: AgentState) -> Dict[str, Any]:
    print("[Agent Node] Shopping Search Agent execution active...")
    updated_items = list(state.get("items_list", []))
    
    for item in updated_items:
        if item.get("status") == "PENDING":
            # Fire our synchronous tool function
            store_data = get_live_jiomart_item(item["product"])
            item["verified_title"] = store_data["title"]
            item["price"] = store_data["price"]
            item["url"] = store_data["url"]
            item["status"] = "VERIFIED"
            
    return {"items_list": updated_items, "next_action": "CONSTRAINT_CHECK"}

# --- Node C: Constraint Solver & Re-Planner Agent ---
def constraint_node(state: AgentState) -> Dict[str, Any]:
    print("[Agent Node] Constraint Solver Agent evaluating boundaries...")
    items = list(state["items_list"])
    budget = state["max_budget"]
    
    subtotal = sum(item.get("price", 0.0) for item in items)
    delivery_fee = 40.00
    grand_total = subtotal + delivery_fee
    
    # RE-PLANNING CONDITION: Budget is exceeded!
    if budget and grand_total > budget:
        print(f"[Alert] Budget exceeded ({grand_total} > {budget}). Re-evaluating cheaper alternatives...")
        # Find the most expensive item to substitute or scale down
        if items:
            priciest_item = max(items, key=lambda x: x.get("price", 0.0))
            if priciest_item.get("price", 0.0) > 40.00 and "pack" not in priciest_item["product"]:
                priciest_item["product"] = f"cheaper small {priciest_item['product']}"
                priciest_item["status"] = "PENDING"  # Re-route item back to search node
                return {"items_list": items, "next_action": "SEARCH", "current_total": grand_total}
                
    return {"items_list": items, "next_action": "INVOICE_READY", "current_total": grand_total}

# --- Build LangGraph State Machine Workflow Graph ---
workflow = StateGraph(AgentState)

workflow.add_node("PlannerNode", planner_node)
workflow.add_node("ShoppingNode", shopping_node)
workflow.add_node("ConstraintNode", constraint_node)

workflow.set_entry_point("PlannerNode")

# Define conditional execution branches routing edges
def route_after_planner(state: AgentState):
    return "ShoppingNode" if state["next_action"] == "SEARCH" else END

def route_after_constraint(state: AgentState):
    return "ShoppingNode" if state["next_action"] == "SEARCH" else END

workflow.add_conditional_edges("PlannerNode", route_after_planner)
workflow.add_node("ShoppingNodeStep", shopping_node)
workflow.add_edge("ShoppingNode", "ConstraintNode")
workflow.add_conditional_edges("ConstraintNode", route_after_constraint)

# Compile graph configuration pipeline instance
compiled_agent_graph = workflow.compile()