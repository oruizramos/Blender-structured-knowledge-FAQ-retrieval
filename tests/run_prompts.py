import json
import sys
from adapters.huggingface_adapter import HuggingFaceAdapter
from fetchers.blender_fetcher import fetch_and_cache
from prompts.evaluator import Evaluator

with open(str(__import__('pathlib').Path(__file__).resolve().parents[1] / 'prompts' / 'templates.json'), "r", encoding="utf-8") as f:
    PROMPTS = json.load(f)

def find_relevant_chunks(chunks, query, top_k=3):
    qtokens = set([w.lower() for w in query.split() if len(w)>3])
    scored = []
    for c in chunks:
        text = c.get('text','').lower()
        score = sum(1 for t in qtokens if t in text)
        scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [c for s,c in scored if s>0][:top_k]
    if not selected:
        return chunks[:top_k]
    return selected

def run(question: str, section_path: str, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
    print('Fetching Blender docs (cached) ...')
    chunks = fetch_and_cache()
    print(f'Loaded {len(chunks)} chunks from cache')

    # find relevant chunks based on the provided section path or naive matching
    relevant = [c for c in chunks if section_path.split('/')[-1].split('.')[0] in c.get('id','')] or find_relevant_chunks(chunks, question, top_k=3)
    context = '\n---\n'.join([c['text'] for c in relevant])

    templates = PROMPTS
    adapter = HuggingFaceAdapter(model=model)

    rows = []
    for name, template in templates.items():
        prompt = template.format(question=question, context=context[:2000])
        print('\n---\nRunning template:', name)
        try:
            resp = adapter.generate(prompt, max_new_tokens=300, temperature=0.2)
            text = resp.get('text','') if isinstance(resp, dict) else str(resp)
        except Exception as e:
            text = f'ERROR: {e}'
        evalr = Evaluator(context).evaluate(text)
        rows.append({
            'template': name,
            'answer': text,
            'relevance': evalr['relevance'],
            'conciseness': evalr['conciseness'],
            'length': evalr['length']
        })
        print('Response preview:', text[:400].replace('\n',' '))
        print('Score:', evalr)

    # save report
    import csv, time
    outp = Path = __import__('pathlib').Path
    report_dir = outp(__file__).resolve().parents[1] / 'data' / 'cache' / 'reports'
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"report_{int(time.time())}.csv"
    import pandas as pd
    pd.DataFrame(rows).to_csv(report_file, index=False)
    print('\nReport saved to', report_file)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tests/run_prompts.py '<question>' '<blender_doc_path>'")
        sys.exit(1)
    question = sys.argv[1]
    section_path = sys.argv[2]
    run(question, section_path)
