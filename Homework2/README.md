# DATA-236 – Homework 2

## Course
DATA-236: Distributed Systems

## Overview
This assignment demonstrates frontend development, backend API implementation, and a stateful multi-agent system using LangGraph.

The project is divided into three main parts:

---

## Part 1: HTML & CSS – Artist Liberty

Designed and styled web pages using HTML and CSS to demonstrate layout structure, styling, and responsiveness.

---

## Part 2: FastAPI – Book Management System

Built a simple CRUD-based Book Management System using FastAPI.

### Implemented Features:
- Add a new book (Title and Author)
- Update book with ID = 1  
  - Title: **Harry Potter**  
  - Author: **J.K. Rowling**
- Delete the book with the highest ID
- Search for a book by title
- Redirect to home page after each operation
- Display updated list dynamically

---

## Part 3: Stateful Agent Graph (LangGraph)

Refactored a sequential agent workflow into a stateful graph-based architecture using the `langgraph` library.

### Key Components:
- `AgentState` using TypedDict (shared memory)
- Planner Node
- Reviewer Node
- Supervisor Node (Routing Logic)
- Conditional edges
- Turn counter to prevent infinite loops

### Workflow:
1. Supervisor routes the task
2. Planner generates proposal
3. Reviewer evaluates proposal
4. If issues → Loop back to Planner
5. If no issues → End execution

This demonstrates dynamic routing and self-correcting agent behavior.

---

## Technologies Used
- Python
- FastAPI
- HTML
- CSS
- LangGraph
- TypedDict


