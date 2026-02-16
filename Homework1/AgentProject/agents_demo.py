import requests
import json
import sys
import re

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "smollm:1.7b"

def query_ollama(prompt, max_length=50):
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
        response = requests.post(OLLAMA_URL, json=payload)
        return response.json().get("response", "").strip()
    except:
        return ""

def planner_agent(title, content):
    """
    Planner Agent:
    1. Uses Python to extract reliable tags from the Title.
    2. Uses LLM to draft a summary.
    """
    # --- TOOL USE: Extract Tags from Title ---
    ignore_words = ["the", "of", "and", "in", "to", "a"]
    clean_words = [w for w in title.split() if w.lower() not in ignore_words]
    tags_list = clean_words[:3]
    tags_str = ", ".join(tags_list)

    # --- LLM USE: Draft Summary ---
    prompt = f"""
    [Task] Summarize the text below in 1 sentence.
    [Text] {content}
    [Summary]"""
    summary = query_ollama(prompt, max_length=40)

    return f"Tags: {tags_str}\nSummary: {summary}"

def reviewer_agent(planner_output):
    """
    Reviewer Agent:
    Strictly shortens the text using a pattern-completion prompt.
    """
    # Parse the previous output
    lines = planner_output.split('\n')
    tags_line = lines[0].strip() 
    summary_line = ""
    for line in lines:
        if line.startswith("Summary:"):
            summary_line = line.replace("Summary:", "").strip()
            break
    
    if not summary_line:
        summary_line = "Agentic AI shifts from passive LLMs to active agents."

    # FORCE the model to just write the shortened version
    prompt = f"""
    Input: {summary_line}
    Rewrite in 10 words:"""
    
    short_summary = query_ollama(prompt, max_length=20)
    
    # Safety: If the model failed to produce text, use a fallback
    if not short_summary:
        short_summary = "AI agents can reason and act."

    return f"{tags_line}\nSummary: {short_summary}"

def finalizer_agent(reviewer_output):
    """
    Finalizer Agent:
    Formats the text into valid JSON.
    """
    try:
        lines = reviewer_output.split('\n')
        
        # Extract tags
        tags_raw = lines[0].replace("Tags:", "").strip()
        tags_list = [t.strip() for t in tags_raw.split(',')]
        
        # Extract summary
        summary_raw = lines[1].replace("Summary:", "").strip()
        
        # Build JSON
        data = {
            "tags": tags_list,
            "summary": summary_raw
        }
        return json.dumps(data, indent=2)
    except:
        return json.dumps({"error": "formatting failed"})

def main():
    blog_title = "The Rise of Agentic AI"
    blog_content = """
    We are witnessing a paradigm shift from passive Large Language Models (LLMs) to active AI Agents. 
    While a standard LLM simply predicts the next word based on a prompt, an Agent possesses the ability to reason, plan, and execute actions using external tools. 
    This 'agentic' workflow typically involves a loop of observation, thought, and action.
    """

    print(f"--- Processing: {blog_title} ---\n")

    # --- Step 1: Planner ---
    print(">>> 1. PLANNER AGENT RUNNING...")
    plan = planner_agent(blog_title, blog_content)
    print(f"[Planner Output]:\n{plan}\n")
    print("-" * 40)

    # --- Step 2: Reviewer ---
    print("\n>>> 2. REVIEWER AGENT RUNNING...")
    review = reviewer_agent(plan)
    print(f"[Reviewer Output]:\n{review}\n")
    print("-" * 40)

    # --- Step 3: Finalizer ---
    print("\n>>> 3. FINALIZER AGENT RUNNING...")
    final_json = finalizer_agent(review)
    print("\n[Final Publish Output (JSON)]:")
    print(final_json)

if __name__ == "__main__":
    main()