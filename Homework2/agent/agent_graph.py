import requests
import json
from typing import TypedDict, Dict, Any, List, Literal, Optional

from langgraph.graph import StateGraph, END


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "smollm:1.7b"


FORCE_ISSUES = True


def query_ollama(prompt: str, max_length: int = 80) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": max_length,
            "stop": ["\n", "User:", "Input:", "Original:"]
        }
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        return response.json().get("response", "").strip()
    except Exception:
        return ""


class AgentState(TypedDict):
    title: str
    content: str
    planner_output: str
    reviewer_output: str
    final_json: Dict[str, Any]
    reviewer_feedback: Dict[str, Any]
    turn_count: int


def _word_count(s: str) -> int:
    return len([w for w in s.strip().split() if w])


def _extract_tags_and_summary(text: str) -> Dict[str, Any]:
    tags: List[str] = []
    summary: str = ""

    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("tags:"):
            raw = line.split(":", 1)[1].strip()
            tags = [t.strip() for t in raw.split(",") if t.strip()]
        elif line.lower().startswith("summary:"):
            summary = line.split(":", 1)[1].strip()

    return {"tags": tags, "summary": summary}


def _validate(tags: List[str], summary: str) -> List[str]:
    issues: List[str] = []
    if len(tags) != 3:
        issues.append("Must have exactly 3 tags.")
    if any((not isinstance(t, str) or not t.strip()) for t in tags):
        issues.append("All tags must be non-empty strings.")
    if not summary or not isinstance(summary, str):
        issues.append("Summary must be a non-empty string.")
    elif _word_count(summary) > 25:
        issues.append("Summary must be <= 25 words.")
    return issues


def planner_agent(title: str, content: str, issues: Optional[List[str]] = None) -> str:
    ignore_words = ["the", "of", "and", "in", "to", "a"]
    clean_words = [w for w in title.split() if w.lower() not in ignore_words]
    tags_list = clean_words[:3]
    tags_str = ", ".join(tags_list) if tags_list else "AI, Agents, LLMs"

    issues_text = ""
    if issues:
        issues_text = "Fix these issues:\n" + "\n".join(f"- {x}" for x in issues)

    prompt = f"""
[Task] Write a ONE-SENTENCE summary of the text in <= 25 words.
{issues_text}
[Text] {content}
[Summary]
""".strip()

    summary = query_ollama(prompt, max_length=60)
    if not summary:
        summary = "AI agents plan, use tools, and act to complete tasks reliably."

    return f"Tags: {tags_str}\nSummary: {summary}"


def reviewer_agent(planner_output: str) -> Dict[str, Any]:
    parsed = _extract_tags_and_summary(planner_output)
    tags = parsed["tags"]
    summary = parsed["summary"]

    if _word_count(summary) > 25:
        words = [w for w in summary.strip().split() if w]
        summary = " ".join(words[:25]).rstrip(".,;:!?")
        if summary.lower().endswith("based on"):
         summary += " the prompt"
        summary += "."

    issues = _validate(tags, summary)
    reviewer_output = f"Tags: {', '.join(tags)}\nSummary: {summary}"

    
    if FORCE_ISSUES:
        issues = issues + ["(TEST) Force reviewer issue to trigger correction loop."]
        return {
            "approved": False,
            "issues": issues,
            "reviewer_output": reviewer_output
        }

    return {
        "approved": len(issues) == 0,
        "issues": issues,
        "reviewer_output": reviewer_output
    }


def finalizer_agent(reviewer_output: str) -> Dict[str, Any]:
    parsed = _extract_tags_and_summary(reviewer_output)
    return {"tags": parsed["tags"], "summary": parsed["summary"]}


def supervisor_node(state: AgentState) -> Dict[str, Any]:
    turn = state.get("turn_count", 0) + 1
    print(f"\n--- SUPERVISOR (turn_count={turn}) ---")
    return {"turn_count": turn}


def planner_node(state: AgentState) -> Dict[str, Any]:
    print("\n--- PLANNER ---")
    issues = state.get("reviewer_feedback", {}).get("issues", [])
    out = planner_agent(state["title"], state["content"], issues=issues)
    print(out)
    return {
        "planner_output": out,
        "reviewer_output": "",
        "reviewer_feedback": {},
        "final_json": {}
    }


def reviewer_node(state: AgentState) -> Dict[str, Any]:
    print("\n--- REVIEWER ---")
    fb = reviewer_agent(state["planner_output"])
    print("Approved:", fb["approved"])
    if fb["issues"]:
        print("Issues:", fb["issues"])
    print(fb["reviewer_output"])
    return {
        "reviewer_feedback": {"approved": fb["approved"], "issues": fb["issues"]},
        "reviewer_output": fb["reviewer_output"]
    }


def finalizer_node(state: AgentState) -> Dict[str, Any]:
    print("\n--- FINALIZER ---")
    j = finalizer_agent(state["reviewer_output"])
    print(json.dumps(j, indent=2))
    return {"final_json": j}


Route = Literal["planner", "reviewer", "finalizer", END]


def router(state: AgentState) -> Route:
    max_turns = 7

    if state.get("final_json") and state.get("reviewer_feedback", {}).get("approved") is True:
        return END

    if state.get("turn_count", 0) >= max_turns:
        return END

    if not state.get("planner_output"):
        return "planner"

    if not state.get("reviewer_output"):
        return "reviewer"

    if not state.get("reviewer_feedback", {}).get("approved", False):
        return "planner"

    return "finalizer"


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("supervisor", supervisor_node)
    g.add_node("planner", planner_node)
    g.add_node("reviewer", reviewer_node)
    g.add_node("finalizer", finalizer_node)

    g.set_entry_point("supervisor")

    g.add_conditional_edges(
        "supervisor",
        router,
        {
            "planner": "planner",
            "reviewer": "reviewer",
            "finalizer": "finalizer",
            END: END,
        },
    )

    g.add_edge("planner", "supervisor")
    g.add_edge("reviewer", "supervisor")
    g.add_edge("finalizer", "supervisor")

    return g.compile()


def main():
    initial_state: AgentState = {
        "title": "The Rise of Agentic AI",
        "content": (
            "We are witnessing a paradigm shift from passive Large Language Models (LLMs) to active AI Agents. "
            "While a standard LLM simply predicts the next word based on a prompt, an Agent can reason, plan, "
            "and execute actions using external tools in an observation-thought-action loop."
        ),
        "planner_output": "",
        "reviewer_output": "",
        "final_json": {},
        "reviewer_feedback": {},
        "turn_count": 0,
    }

    app = build_graph()

    print("\n=== RUN GRAPH ===")
    final_state = app.invoke(initial_state)

    print("\n=== FINAL STATE OUTPUT ===")
    if final_state.get("reviewer_feedback", {}).get("approved"):
        print(json.dumps(final_state["final_json"], indent=2))
    else:
        print("Did not reach approval within max turns.")
        print("Last feedback:", final_state.get("reviewer_feedback"))
        print("Last proposal:", final_state.get("final_json") or final_state.get("reviewer_output"))


if __name__ == "__main__":
    main()


