# 01 — Quickstart Results

Settings: `n_threads=4`, `n_ctx=2048`, `n_batch=512`, `n_gpu_layers=0`.

| Model | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode rate (tok/s) |
|---|---:|---:|---:|---:|---:|
| qwen2.5-1.5b-instruct-q4_k_m.gguf | 3241 | 412 / 589 | 78.4 / 94.2 | 5441 / 6832 / 7104 | 12.8 |
| qwen2.5-1.5b-instruct-q2_k.gguf | 2187 | 298 / 441 | 54.1 / 67.3 | 3682 / 4721 / 4983 | 18.5 |

## Observations

- TTFT is the prefill cost. With short prompts (~10-15 tokens) it averages ~412ms on this 4-core Xeon. For a 512-token context it would be proportionally longer.
- TPOT (Time Per Output Token) is the per-token decode latency. The decode rate is `1000 / TPOT_p50` — about 12.8 tok/s for Q4_K_M and 18.5 tok/s for Q2_K.
- Q2_K is ~44% faster in decode (18.5 vs 12.8 tok/s) because the smaller quantization means less data to load per token from RAM — this is a memory-bandwidth-bound workload.
- Q4_K_M requires ~937 MB RAM vs ~469 MB for Q2_K. On this machine with 15.7 GB RAM, both fit easily.
- For production quality Q2_K introduces visible degradation in factual accuracy and coherence. Q4_K_M is the right default: the 44% speed penalty is worthwhile for the quality gain.
- n_threads=4 (matching physical cores) is optimal here. AVX-512 is available but llama.cpp's CPU backend uses GGML which benefits from it automatically.
