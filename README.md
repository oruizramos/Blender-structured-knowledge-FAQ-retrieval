# PromptLab – Automated Prompt Engineering Toolkit

PromptLab is a Python experimental framework for "Systematic prompt engineering and evaluation". It showcases how to design, test, and analyze prompts with documentation content (in this case, Blender's manual), automated testing, and evaluation. 

## Features / Prompt Types

* Chain-of-thought 
* Persona tutor
* Few-shot 
* JSON-schema enforcement
* Debate mode 
* Short-bullets
* Checklist-with-verification

## Tech Stack

- **Python** – core framework, scripting, automation  
- **Hugging Face Inference API** – LLM responses (online, token-based)  
- **JSON / YAML** – template and configuration management  
- **Requests / Caching** – documentation fetching and local caching  
- **Command-line tooling** – lightweight, portable execution and testing  

## Quickstart:

1. Create a venv and install:

```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
```

2. Export your Hugging Face token:

```
   export HF_TOKEN=hf_xxx...   # macOS/Linux
   set HF_TOKEN=hf_xxx...      # Windows CMD
   $env:HF_TOKEN='hf_xxx...'   # PowerShell
```

3. Run an example:

```
   python tests/run_prompts.py "How do I add a Subdivision Surface modifier to a mesh in Blender?" modeling/modifiers/generate/subdivision_surface.html
```

## Notes:
- The fetcher caches docs in data/cache/blender_docs_cache.json to speed repeated runs.
- The templates live in prompts/templates.json; add new templates there to experiment.
- The evaluator is intentionally lightweight; consider embedding similarity for stronger grounding checks.
- Caches speeds up repeated runs and allows offline testing.
- Fully extensible to other documentation sets (not just Blender's).

