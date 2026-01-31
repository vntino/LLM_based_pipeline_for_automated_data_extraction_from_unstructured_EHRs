import ctypes
ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)

import asyncio, json, time, pathlib, httpx, pandas as pd
from typing import Any, Dict
from tenacity import retry, wait_exponential, stop_after_attempt, RetryError
from euroscore2_model_strict_grammar import EuroScore2Strict as Euro
from pydantic import ValidationError
import re

# ── configuration ──────────────────────────────────────────────────────────
WORKDIR    = pathlib.Path(r"WORKING_DIRECTORY")
OUTPUTDIR  = pathlib.Path(r"OUTPUT_DIRECTORY")
XLSX_FILE  = WORKDIR / "medical_reports.xlsx"
PROMPT_TXT = WORKDIR / "prompt.txt"
SYSTEM_TXT = WORKDIR / "system.txt"

OLLAMA_URL = "LOCAL_OLLAMA_ENDPOINT_URL"
MODEL      = "OLLAMA_LLM_NAME"
TEMPERATURE = 0       
CONCURRENCY    = 4
MAX_ALGO_RETRY = 5
HTTP_TIMEOUT   = 120

SYSTEM_TXT_MESSAGE = SYSTEM_TXT.read_text(encoding="utf-8").strip()
SYSTEM_PROMPT = PROMPT_TXT.read_text(encoding="utf-8").strip()
SCHEMA_DICT   = Euro.model_json_schema()     

# ── result stores ──────────────────────────────────────────────────────────
raw_rows, json_rows, pyd_rows = [], [], []

# ── helpers to return response and metrics ─────────────────────────────────
def _post(payload: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """Send request → return (answer_text, meta_dict)."""
    t0 = time.perf_counter()
    r = httpx.post(OLLAMA_URL, json=payload,
                   timeout=HTTP_TIMEOUT, trust_env=False)
    r.raise_for_status()
    meta = r.json()                       
    if isinstance(meta.get("total_duration"), int): meta["total_duration"] = meta["total_duration"] / 1_000_000_000
    meta.setdefault("total_duration", time.perf_counter() - t0)
    return meta["response"], meta         

@retry(wait=wait_exponential(1, 1, 8), stop=stop_after_attempt(4))
def ask_plain(report: str) -> tuple[str, Dict[str, Any]]:
    payload = {
        "model": MODEL,
        "system": SYSTEM_TXT_MESSAGE,
        "prompt": SYSTEM_PROMPT.replace("{REPORT}", report),
        "options": {"temperature": TEMPERATURE, "num_ctx": 8000},
        "stream": False
    }
    return _post(payload)

@retry(wait=wait_exponential(1, 1, 8), stop=stop_after_attempt(4))
def ask_grammar(report: str) -> tuple[str, Dict[str, Any]]:
    payload = {
        "model": MODEL,
        "system": SYSTEM_TXT_MESSAGE,
        "prompt": SYSTEM_PROMPT.replace("{REPORT}", report),
        "format": "json",
        "schema": SCHEMA_DICT,
        "options": {"temperature": TEMPERATURE, "num_ctx": 8000},
        "stream": False
    }
    return _post(payload)

# ── helper to strip <think>…</think> blocks ────────────────────────────────
def strip_think_block(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# ── co-driver  ─────────────────────────────────────────────────────────────
async def worker(q: asyncio.Queue):
    while True:
        item = await q.get()
        if item is None:
            q.task_done(); break
        idx, text = item
        retries = 0
        while retries < MAX_ALGO_RETRY:
            try:
                answer, meta = (ask_plain(text) if retries == 0
                        else ask_grammar(text))
            except RetryError as e:
                answer, meta = f"<<HTTP failure {e}>>", {"prompt_eval_count": None,
                                                 "total_duration": None}

            # Clean the model response by removing any <think>…</think> block
            clean_answer = strip_think_block(answer)

            base = {
                "report_idx": idx,
                "retry_no": retries,
                "raw_output": answer,  
                "clean_output": clean_answer,  
                "prompt_tokens": meta.get("prompt_eval_count"),
                "latency_s":    meta.get("total_duration")
            }       

            # JSON check
            try:
                obj = json.loads(clean_answer)
                json_rows.append({**base, **obj})
            except json.JSONDecodeError:
                raw_rows.append({**base, "JSON_valid": False, "pydantic_valid": False})
                retries += 1
                continue

            # Pydantic check
            try:
                pyd = Euro.model_validate_json(clean_answer).model_dump()
                pyd_rows.append({**base, **pyd, "number_retries": retries})
                raw_rows.append({**base, "JSON_valid": True, "pydantic_valid": True})
                break
            except ValidationError as e:
                raw_rows.append({**base, "JSON_valid": True,
                                 "pydantic_valid": False,
                                 "pydantic_errors": e.errors()})
                retries += 1
        q.task_done()

# ── main driver ────────────────────────────────────────────────────────────

async def main():
    texts = pd.read_excel(XLSX_FILE)["full_text"].astype(str).tolist()
    q = asyncio.Queue()
    for i, t in enumerate(texts, start=1):
        await q.put((i, t))

    workers = [asyncio.create_task(worker(q)) for _ in range(CONCURRENCY)]
    await q.join()
    for _ in workers: await q.put(None)
    await asyncio.gather(*workers)

    ts = time.strftime("%Y%m%d_%H%M%S")
    pd.DataFrame(raw_rows).to_csv(OUTPUTDIR / f"raw_{ts}_OLLAMA_LLM_NAME.csv",  index=False)
    pd.DataFrame(json_rows).to_csv(OUTPUTDIR / f"json_{ts}_OLLAMA_LLM_NAME.csv", index=False)
    pd.DataFrame(pyd_rows).to_csv(OUTPUTDIR / f"pyd_{ts}_OLLAMA_LLM_NAME.csv",  index=False)
    print(f"Done — {len(pyd_rows)}/{len(texts)} reports are Pydantic-valid.")

if __name__ == "__main__":
    asyncio.run(main())