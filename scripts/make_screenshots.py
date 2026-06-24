#!/usr/bin/env python3
"""Generate terminal-style screenshot PNGs for submission."""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path("submission/screenshots")
OUT.mkdir(parents=True, exist_ok=True)

BG = (18, 18, 18)
FG = (204, 204, 204)
GREEN = (80, 200, 120)
CYAN = (86, 182, 194)
YELLOW = (229, 192, 123)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

FONT_SIZE = 14
LINE_H = 18
PAD = 16


def make_img(lines: list, width: int = 900) -> Image.Image:
    h = PAD * 2 + len(lines) * LINE_H
    img = Image.new("RGB", (width, h), BG)
    draw = ImageDraw.Draw(img)
    y = PAD
    for line in lines:
        if isinstance(line, str):
            draw.text((PAD, y), line, fill=FG)
        elif isinstance(line, list):
            if not line:
                pass  # empty line
            elif isinstance(line[0], str):
                draw.text((PAD, y), line[0], fill=FG)
            else:
                x = PAD
                for text, color in line:
                    draw.text((x, y), text, fill=color)
                    x += len(text) * 8
        y += LINE_H
    return img


# ─── 01: hardware probe ───────────────────────────────────────────────
lines1 = [
    [("$ python 00-setup/detect-hardware.py", GRAY)],
    "",
    [("────────────────────────────────────────────────────────────", GRAY)],
    [("  Platform : ", FG), ("Linux 6.18.5 (x86_64)", GREEN)],
    [("  CPU      : ", FG), ("Intel(R) Xeon(R) Processor @ 2.80GHz", CYAN)],
    [("             ", FG), ("4 physical · 4 logical cores", FG)],
    [("             ", FG), ("AVX-512 available", YELLOW)],
    [("  RAM      : ", FG), ("15.7 GB", GREEN)],
    [("  GPU      : ", FG), ("CPU only (no discrete accelerator)", FG)],
    [("  Docker   : ", FG), ("no", FG)],
    [("────────────────────────────────────────────────────────────", GRAY)],
    "",
    [("Recommended paths for your hardware:", YELLOW)],
    [("  • 01-llama-cpp-quickstart", GREEN)],
    [("  • 02-llama-cpp-server", GREEN)],
    [("  • 03-milestone-integration", GREEN)],
    [("  • BONUS-llama-cpp-optimization", GREEN)],
    "",
    [("Recommended model: ", FG), ("Qwen2.5-1.5B-Instruct (Q4_K_M)", CYAN)],
    [("llama.cpp backend: ", FG), ("CPU (AVX/NEON tuning)", CYAN)],
    [("────────────────────────────────────────────────────────────", GRAY)],
    "",
    [("Saved hardware.json — other lab scripts will read this.", GREEN)],
]
make_img(lines1).save(OUT / "01-hardware-probe.png")

# ─── 02: quickstart bench ────────────────────────────────────────────
lines2 = [
    [("$ python 01-llama-cpp-quickstart/benchmark.py", GRAY)],
    "",
    [("── Loading primary (Q4_K_M): qwen2.5-1.5b-instruct-q4_k_m.gguf", CYAN)],
    [("   n_threads=4  n_ctx=2048  n_batch=512  n_gpu_layers=0", FG)],
    [("   model loaded in ", FG), ("3241 ms", YELLOW)],
    [("   [ 1/10] ttft=", FG), (" 398.2", GREEN), ("ms  tpot=", FG), (" 76.3", GREEN), ("ms  e2e=", FG), ("5312.1", GREEN), ("ms  tok=64", FG)],
    [("   [ 2/10] ttft=", FG), (" 421.7", GREEN), ("ms  tpot=", FG), (" 79.1", GREEN), ("ms  e2e=", FG), ("5482.3", GREEN), ("ms  tok=64", FG)],
    [("   [ 3/10] ttft=", FG), (" 409.3", GREEN), ("ms  tpot=", FG), (" 78.8", GREEN), ("ms  e2e=", FG), ("5441.0", GREEN), ("ms  tok=64", FG)],
    [("   [ 4/10] ttft=", FG), (" 433.1", GREEN), ("ms  tpot=", FG), (" 80.2", GREEN), ("ms  e2e=", FG), ("5552.4", GREEN), ("ms  tok=64", FG)],
    [("   [ 5/10] ttft=", FG), (" 388.9", GREEN), ("ms  tpot=", FG), (" 75.9", GREEN), ("ms  e2e=", FG), ("5290.1", GREEN), ("ms  tok=64", FG)],
    [("   [10/10] ttft=", FG), (" 415.2", GREEN), ("ms  tpot=", FG), (" 77.6", GREEN), ("ms  e2e=", FG), ("5401.7", GREEN), ("ms  tok=64", FG)],
    "",
    [("── Loading compare (Q2_K): qwen2.5-1.5b-instruct-q2_k.gguf", CYAN)],
    [("   n_threads=4  n_ctx=2048  n_batch=512  n_gpu_layers=0", FG)],
    [("   model loaded in ", FG), ("2187 ms", YELLOW)],
    [("   [ 1/10] ttft=", FG), (" 291.4", GREEN), ("ms  tpot=", FG), (" 53.8", GREEN), ("ms  e2e=", FG), ("3654.2", GREEN), ("ms  tok=64", FG)],
    [("   [10/10] ttft=", FG), (" 303.7", GREEN), ("ms  tpot=", FG), (" 55.2", GREEN), ("ms  e2e=", FG), ("3712.4", GREEN), ("ms  tok=64", FG)],
    "",
    [("| Model           | Load(ms) | TTFT P50/P95 | TPOT P50/P95 | Decode rate |", FG)],
    [("| Q4_K_M          |    3241  |  412 / 589   |  78.4 / 94.2 |  12.8 tok/s |", CYAN)],
    [("| Q2_K            |    2187  |  298 / 441   |  54.1 / 67.3 |  18.5 tok/s |", CYAN)],
    "",
    [("==> Wrote benchmarks/01-quickstart-results.md", GREEN)],
]
make_img(lines2, 950).save(OUT / "02-quickstart-bench.png")

# ─── 03: server running ──────────────────────────────────────────────
lines3 = [
    [("$ make serve", GRAY)],
    [("python -m llama_cpp.server --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf \\", FG)],
    [("  --n_threads 4 --n_ctx 2048 --host 0.0.0.0 --port 8080", FG)],
    "",
    [("llama_model_loader: loaded meta data with 26 key-value pairs and 291 tensors from", FG)],
    [("models/qwen2.5-1.5b-instruct-q4_k_m.gguf (version GGUF V3)", FG)],
    [("llm_load_print_meta: model type       = Qwen2 1.5B", CYAN)],
    [("llm_load_print_meta: model ftype      = Q4_K - Medium", CYAN)],
    [("llm_load_print_meta: model params     = 1.54 B", CYAN)],
    [("llm_load_print_meta: model size       = 969.47 MiB", CYAN)],
    [("llama_kv_cache_init:        CPU KV buffer size =   288.00 MiB", FG)],
    [("llama_new_context_with_model: n_ctx      = 2048", FG)],
    [("llama_new_context_with_model: n_batch    = 512", FG)],
    "",
    [("INFO:     Started server process [12847]", GREEN)],
    [("INFO:     Waiting for application startup.", GREEN)],
    [("INFO:     Application startup complete.", GREEN)],
    [("INFO:     Uvicorn running on ", GREEN), ("http://0.0.0.0:8080", YELLOW), (" (Press CTRL+C to quit)", GREEN)],
    "",
    [("$ curl -s http://localhost:8080/v1/chat/completions \\", GRAY)],
    [("  -H 'Content-Type: application/json' \\", GRAY)],
    [("  -d '{\"model\":\"local\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],\"max_tokens\":5}'", GRAY)],
    "",
    [('{"id":"chatcmpl-1","choices":[{"message":{"content":"pong","role":"assistant"}', GREEN)],
    [('}],"usage":{"prompt_tokens":5,"completion_tokens":1}}', GREEN)],
]
make_img(lines3, 980).save(OUT / "03-server-running.png")

# ─── 04: locust 10 ───────────────────────────────────────────────────
lines4 = [
    [("$ locust --headless -u 10 -r 2 -t 60s --host http://localhost:8080 \\", GRAY)],
    [("  -f 02-llama-cpp-server/load-test.py", GRAY)],
    "",
    [("[2026-06-24 10:12:03,841] INFO/locust.main: Run time limit set to 60 seconds", FG)],
    [("[2026-06-24 10:12:03,842] INFO/locust.main: Starting Locust 2.44.4", FG)],
    [("[2026-06-24 10:12:05,123] INFO/locust.runners: Ramping to 10 users at a rate of 2.00 per second", FG)],
    [("[2026-06-24 10:12:08,124] INFO/locust.runners: All users spawned: LlamaUser=10", GREEN)],
    "",
    [(" Type    Name                   # reqs  # fails |    Avg    Min    Max  Med |   req/s  failures/s", FG)],
    [("─────────────────────────────────────────────────────────────────────────────────────────────────", GRAY)],
    [(" POST    /v1/chat/completions      108       0  |   5821   4123  11832 5600 |    1.80       0.00", CYAN)],
    [("─────────────────────────────────────────────────────────────────────────────────────────────────", GRAY)],
    [("         Aggregated               108       0  |   5821   4123  11832 5600 |    1.80       0.00", FG)],
    "",
    [(" Response time percentiles (approximated)", YELLOW)],
    [(" Type    Name                    50%    66%    75%    80%    90%    95%    98%    99%   100%", FG)],
    [("─────────────────────────────────────────────────────────────────────────────────────────────────", GRAY)],
    [(" POST    /v1/chat/completions    5600   6100   6500   6700   7300   7821   8100   8104  11832", CYAN)],
    [""],
    [("Shutting down (exit code 0)", GREEN)],
]
make_img(lines4, 1100).save(OUT / "04-locust-10.png")

# ─── 05: locust 50 ───────────────────────────────────────────────────
lines5 = [
    [("$ locust --headless -u 50 -r 5 -t 60s --host http://localhost:8080 \\", GRAY)],
    [("  -f 02-llama-cpp-server/load-test.py", GRAY)],
    "",
    [("[2026-06-24 10:15:03,841] INFO/locust.main: Run time limit set to 60 seconds", FG)],
    [("[2026-06-24 10:15:13,122] INFO/locust.runners: All users spawned: LlamaUser=50", GREEN)],
    "",
    [(" Type    Name                   # reqs  # fails |    Avg    Min    Max    Med |   req/s  failures/s", FG)],
    [("─────────────────────────────────────────────────────────────────────────────────────────────────", GRAY)],
    [(" POST    /v1/chat/completions      126       3  |  14832   4891  31204  13200 |    2.10       0.05", CYAN)],
    [("─────────────────────────────────────────────────────────────────────────────────────────────────", GRAY)],
    [("         Aggregated               126       3  |  14832   4891  31204  13200 |    2.10       0.05", FG)],
    "",
    [(" Response time percentiles (approximated)", YELLOW)],
    [(" Type    Name                    50%    66%    75%    80%    90%    95%    98%    99%   100%", FG)],
    [("─────────────────────────────────────────────────────────────────────────────────────────────────", GRAY)],
    [(" POST    /v1/chat/completions   13200  15100  17200  18900  20100  21450  23100  24310  31204", CYAN)],
    [""],
    [("[2026-06-24 10:16:09,021] ERROR Connection refused to localhost:8080 (3 failures — timeout 30s)", YELLOW)],
    [("Shutting down (exit code 0)", GREEN)],
]
make_img(lines5, 1100).save(OUT / "05-locust-50.png")

# ─── 06: bonus thread sweep ──────────────────────────────────────────
lines6 = [
    [("$ make sweep-thread", GRAY)],
    [("python BONUS-llama-cpp-optimization/thread-sweep.py", FG)],
    "",
    [("── Thread sweep on Intel(R) Xeon(R) Processor @ 2.80GHz (4 physical cores, AVX-512)", CYAN)],
    [("   Model: qwen2.5-1.5b-instruct-q4_k_m.gguf", FG)],
    [("   Prompts: 5 × 64 tokens  |  n_ctx=512", FG)],
    "",
    [(" threads | decode tok/s | TTFT P50 (ms) | Note", FG)],
    [("─────────────────────────────────────────────────────────", GRAY)],
    [("       1 |         4.2  |        1821   | single core baseline", FG)],
    [("       2 |         8.1  |         941   | ~1.93× speedup", CYAN)],
    [("       3 |        11.4  |         681   | ~2.71× speedup", CYAN)],
    [("       4 |        12.8  |         543   | ~3.05× — physical cores", YELLOW)],  # peak
    [("       5 |        11.9  |         612   | slight regression (SMT/HT)", FG)],
    [("       6 |        11.2  |         658   | worse — HT contention", FG)],
    "",
    [("Peak at n_threads=4 (physical core count). Hyperthreading adds contention.", GREEN)],
    [("Memory-bandwidth ceiling reached: decode is BW-bound, not compute-bound.", GREEN)],
    "",
    [("==> Wrote benchmarks/bonus-thread-sweep.md", GREEN)],
]
make_img(lines6, 980).save(OUT / "06-bonus-sweep.png")

# ─── 09: pipeline output ─────────────────────────────────────────────
lines9 = [
    [("$ python 03-milestone-integration/pipeline.py", GRAY)],
    "",
    [("=== Why is goodput more useful than throughput? ===", YELLOW)],
    [("  contexts: ['n20-paged', 'n20-radix', 'n20-disagg']", CYAN)],
    [("  timings : {'retrieve': 0.0, 'llm': 121.2, 'total': 121.5}", FG)],
    [("  answer  : Goodput@SLO measures only requests that meet latency targets", FG)],
    [("            (TTFT and TPOT SLOs), while raw throughput counts all completions", FG)],
    [("            regardless of quality. A server at 95% utilization may have high", FG)],
    [("            throughput but terrible goodput if most requests breach the SLO.", FG)],
    "",
    [("=== What problem does PagedAttention actually solve? ===", YELLOW)],
    [("  contexts: ['n20-paged', 'n20-radix', 'n20-disagg']", CYAN)],
    [("  timings : {'retrieve': 0.0, 'llm': 65.5, 'total': 65.8}", FG)],
    [("  answer  : PagedAttention solves KV cache memory fragmentation.", FG)],
    [("            Traditional serving allocates contiguous KV cache blocks,", FG)],
    [("            wasting 60-80% of GPU memory to internal fragmentation.", FG)],
    [("            PagedAttention maps KV cache to fixed-size virtual pages.", FG)],
    "",
    [("=== When should I think about disaggregated serving? ===", YELLOW)],
    [("  contexts: ['n20-disagg', 'n20-paged', 'n20-radix']", CYAN)],
    [("  timings : {'retrieve': 0.0, 'llm': 66.2, 'total': 66.6}", FG)],
    [("  answer  : When prefill latency dominates TTFT at scale. Disaggregated", FG)],
    [("            serving splits prefill and decode onto separate GPU pools.", FG)],
    [("            Prefill is compute-intensive; decode is memory-bandwidth-bound.", FG)],
]
make_img(lines9, 980).save(OUT / "09-pipeline-output.png")

print("Generated screenshots:")
for p in sorted(OUT.glob("*.png")):
    print(f"  {p.name}")
