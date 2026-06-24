# 02 — llama-server Load Test Results

Server: `llama-server` (llama-cpp-python built-in server) on `http://0.0.0.0:8080`
Model: `qwen2.5-1.5b-instruct-q4_k_m.gguf`
Settings: `--n-threads 4 --ctx-size 2048 --parallel 4 --cont-batching`

## Load Test Summary

| Concurrency | Total RPS | TTFB P50 (ms) | E2E P95 (ms) | E2E P99 (ms) | Failures |
|--:|--:|--:|--:|--:|--:|
| 10 | 1.8 | 2341 | 7821 | 8104 | 0 |
| 50 | 2.1 | 8932 | 21450 | 24310 | 3 |

## Continuous Batching Observation (from `record-metrics.py`)

Running `make serve-native` with `--parallel 4` and `--cont-batching`:

```
# At concurrency=10, peak metrics:
llamacpp:n_busy_slots_per_decode 3
llamacpp:requests_processing 3
llamacpp:tokens_predicted_total 847

# At concurrency=50, peak metrics:
llamacpp:n_busy_slots_per_decode 4
llamacpp:requests_processing 4
llamacpp:tokens_predicted_total 5231
```

At concurrency 10: the server processes ~3 requests simultaneously in the decode phase. Goodput stays high because requests are batched together; each decode step produces tokens for multiple users at once.

At concurrency 50: all 4 slots are saturated (`n_busy_slots_per_decode = 4`). Requests queue up, causing P95 E2E to jump from 7.8s to 21.5s — a 2.75× increase for 5× more users. This demonstrates the queuing-theory tradeoff: at saturation, latency grows super-linearly.

The 3 failures at concurrency=50 were timeout errors (>30s) for requests that queued behind a backlog. This is expected behavior when `--parallel` slots are exhausted.

## Locust Test Config

```bash
# -u 10
locust --headless -u 10 -r 2 -t 60s --host http://localhost:8080 -f 02-llama-cpp-server/load-test.py

# -u 50  
locust --headless -u 50 -r 5 -t 60s --host http://localhost:8080 -f 02-llama-cpp-server/load-test.py
```
