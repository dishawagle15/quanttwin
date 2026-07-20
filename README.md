# QuantTwin 

**An AI-powered quantitative architecture and modernization IDE.**

QuantTwin is a specialized development environment designed to bridge the gap between legacy quantitative finance systems and modern data science stacks. It ingests legacy codebases, maps their structural dependencies, mathematically recognizes underlying stochastic models, and modernizes discrete loops into highly optimized, vectorized implementations.
## Key Features

* **AST Architecture Mapping:** Utilizes `tree-sitter` to parse C++ and Python source files, extracting functions, variables, and structural dependencies without executing the code.
* **Interactive Dependency Graph:** Renders a dynamic, node-based visualization of the quantitative pipeline (e.g., Pricing Engines to Monte Carlo Simulators) using `@xyflow/react`.
* **Mathematical Pattern Recognition:** Analyzes source code to identify standard financial models (e.g., Geometric Brownian Motion, Ornstein-Uhlenbeck processes) and renders the exact stochastic differential equations in KaTeX (e.g., dS = \mu Sdt + \sigma SdW).
* **Vectorized Modernization:** Uses LLMs with strict system prompts to translate legacy discrete C++ loops into modern, highly optimized `SciPy` and `NumPy` logic.
* **Trust Meter Guardrails:** Displays AI confidence scores and explicit mathematical evidence to ensure the generated outputs remain strictly grounded in the source logic.

## Tech Stack

**Frontend (`apps/web`)**
* Next.js 15 (React)
* Tailwind CSS (Custom flat, dark-mode-first IDE aesthetic)
* React Flow (Dependency Visualization)
* Monaco Editor (Syntax Highlighting)
* KaTeX (LaTeX Equation Rendering)

**Backend (`apps/api`)**
* FastAPI (Python 3.13+)
* Tree-sitter (AST Parsing)
* OpenAI API (Codex/GPT-4 for translation and summarization)
* Pydantic (Strict Data Validation)

---
## How I used OpenAI Models

QuantTwin leverages the latest OpenAI capabilities to transform legacy quantitative code into modern, optimized Python.

* **Codex for Code Transformation:** We utilize Codex’s specialized code-understanding capabilities to interpret legacy C++ loops. By feeding the AST-parsed logic into Codex with custom system prompts, the model accurately identifies discrete iterations and maps them to their mathematically equivalent NumPy/SciPy vectorized operations.
* **GPT-5.6 for Structural Synthesis:** We leverage the reasoning power of GPT-5.6 to perform high-level analysis on the codebase. It acts as the "Architectural Brain" of the project—interpreting the structural dependencies extracted by tree-sitter, summarizing complex quantitative models, and generating the documentation and KaTeX equation patterns that drive our Inspector panel.

## Getting Started (Local Development)

QuantTwin is structured as a monorepo containing both the Next.js frontend and the FastAPI backend. You will need two terminal instances to run the application locally.

### 1. Start the Backend API
The backend requires Python 3.13+ and handles the AST parsing and LLM communication.

```bash
# Navigate to the API directory
cd apps/api

# Create and activate a virtual environment (macOS/Linux)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API Key
export OPENAI_API_KEY="your-api-key-here"

# Start the FastAPI server
uvicorn app.main:app --reload
