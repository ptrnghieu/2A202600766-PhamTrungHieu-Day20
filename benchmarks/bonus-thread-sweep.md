# Bonus — Thread Sweep Results

Hardware: Intel(R) Xeon(R) Processor @ 2.80GHz, 4 physical cores, AVX-512
Model: `qwen2.5-1.5b-instruct-q4_k_m.gguf`
Settings: `n_ctx=512`, `n_batch=512`, `n_gpu_layers=0`, 5 prompts × 64 tokens each

## Results

| n_threads | Decode (tok/s) | TTFT P50 (ms) | vs baseline |
|--:|--:|--:|--:|
| 1 | 4.2 | 1821 | 1.00× |
| 2 | 8.1 | 941 | 1.93× |
| 3 | 11.4 | 681 | 2.71× |
| **4** | **12.8** | **543** | **3.05× (peak)** |
| 5 | 11.9 | 612 | 2.83× |
| 6 | 11.2 | 658 | 2.67× |

## Observations

Peak decode throughput is at **n_threads=4** (matching physical core count), yielding 12.8 tok/s.

Going above 4 threads causes a regression:
- n_threads=5 → 11.9 tok/s (−7%)
- n_threads=6 → 11.2 tok/s (−12%)

This is the classic memory-bandwidth ceiling pattern:
1. GGML's matrix-vector multiply (the core of autoregressive decode) is **memory-bandwidth bound**, not compute bound. Each token requires loading the full model weight matrix from RAM.
2. More threads don't help once all memory channels are saturated — they add synchronization overhead instead.
3. On this 4-core Xeon, AVX-512 instructions load 512 bits per cycle. Adding hyperthreaded (logical) threads creates cache-line contention in L2/L3 cache, hurting throughput.

Recommendation: set `n_threads = physical_core_count` for CPU-only serving with llama.cpp.
