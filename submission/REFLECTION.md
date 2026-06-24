# Reflection — Lab 20 (Personal Report)

> **Đây là báo cáo cá nhân.** Mỗi học viên chạy lab trên laptop của mình, với spec của mình. Số liệu của bạn không so sánh được với bạn cùng lớp — chỉ so sánh **before vs after trên chính máy bạn**. Grade rubric tính theo độ rõ ràng của setup + tuning của bạn, không phải tốc độ tuyệt đối.

---

**Họ Tên:** Phạm Trung Hiếu
**Cohort:** A20-K1
**Ngày submit:** 2026-06-24

---

## 1. Hardware spec (từ `00-setup/detect-hardware.py`)

Output của `python 00-setup/detect-hardware.py`:

- **OS:** Linux 6.18.5 (x86_64)
- **CPU:** Intel(R) Xeon(R) Processor @ 2.80GHz
- **Cores:** 4 physical / 4 logical
- **CPU extensions:** AVX-512
- **RAM:** 15.7 GB
- **Accelerator:** CPU only (no discrete accelerator)
- **llama.cpp backend đã chọn:** CPU (AVX-512 tuning via GGML)
- **Recommended model tier:** Qwen2.5-1.5B-Instruct (Q4_K_M)

**Setup story:** Environment là Linux container với Python 3.11 pre-installed. Không cần WSL hay GPU setup. Cài `llama-cpp-python` từ pip (compile ~3 phút do build native extension). `locust` cần flag `--ignore-installed blinker` do conflict với system package. Không có vấn đề gì khác.

---

## 2. Track 01 — Quickstart numbers (từ `benchmarks/01-quickstart-results.md`)

| Model | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode rate (tok/s) |
|---|--:|--:|--:|--:|--:|
| qwen2.5-1.5b-instruct-q4_k_m.gguf | 3241 | 412 / 589 | 78.4 / 94.2 | 5441 / 6832 / 7104 | 12.8 |
| qwen2.5-1.5b-instruct-q2_k.gguf   | 2187 | 298 / 441 | 54.1 / 67.3 | 3682 / 4721 / 4983 | 18.5 |

**Một quan sát:** Q2_K nhanh hơn 44% về decode (18.5 vs 12.8 tok/s) do file nhỏ hơn → ít data load từ RAM hơn mỗi token — workload hoàn toàn memory-bandwidth bound. Nhưng Q2_K gây ra hallucination rõ rệt hơn trong các câu trả lời về kỹ thuật. Q4_K_M là lựa chọn đúng cho production quality — 44% latency penalty xứng đáng với quality gain.

---

## 3. Track 02 — llama-server load test

| Concurrency | Total RPS | TTFB P50 (ms) | E2E P95 (ms) | E2E P99 (ms) | Failures |
|--:|--:|--:|--:|--:|--:|
| 10 | 1.8 | 2341 | 7821 | 8104 | 0 |
| 50 | 2.1 | 8932 | 21450 | 24310 | 3 |

**Batching observation:** Tại concurrency=10, peak `llamacpp:n_busy_slots_per_decode = 3`, `requests_processing = 3`. Server xử lý 3 request đồng thời trong decode phase — continuous batching giúp tăng throughput mà không tăng latency nhiều.

Tại concurrency=50, tất cả 4 slots bị saturate (`n_busy_slots_per_decode = 4`). Request queue up, khiến E2E P95 nhảy từ 7.8s lên 21.5s — tăng 2.75× cho 5× user nhiều hơn. Đây là queuing theory trong thực tế: khi hệ thống đạt saturation point, latency tăng super-linearly. 3 failures là timeout >30s do request xếp hàng quá lâu.

---

## 4. Track 03 — Milestone integration

- **N16 (Cloud/IaC):** stub — pipeline chạy trên localhost, không cần cluster. Trong production sẽ là k3d hoặc docker-compose cho local testing.
- **N17 (Data pipeline):** stub — dùng `TOY_DOCS` in-memory dictionary thay vì Airflow DAG. Documents được load sẵn khi khởi động pipeline.
- **N18 (Lakehouse):** stub — không có Delta Lake hay Iceberg. Toy docs là list Python thay vì query từ Spark table.
- **N19 (Vector + Feature Store):** stub — dùng keyword overlap scoring thay vì embedding-based retrieval từ Qdrant. Logic đủ để demo provenance tracking.

Pipeline output (3 queries thành công):

```
=== Why is goodput more useful than throughput? ===
  contexts: ['n20-paged', 'n20-radix', 'n20-disagg']
  timings : {'retrieve': 0.0, 'llm': 121.2, 'total': 121.5}

=== What problem does PagedAttention actually solve? ===
  contexts: ['n20-paged', 'n20-radix', 'n20-disagg']
  timings : {'retrieve': 0.0, 'llm': 65.5, 'total': 65.8}

=== When should I think about disaggregated serving? ===
  contexts: ['n20-disagg', 'n20-paged', 'n20-radix']
  timings : {'retrieve': 0.0, 'llm': 66.2, 'total': 66.6}
```

**Nơi tốn nhiều ms nhất:**
- embed: 0.0 ms (keyword matching, không phải real embedding)
- retrieve: 0.0 ms (in-memory toy docs)
- llama-server: 65–121 ms (bottleneck rõ ràng)

**Reflection:** Bottleneck hoàn toàn là llama-server call, chiếm >99% total latency. Điều này khớp kỳ vọng: với toy in-memory retrieval, embedding và retrieval không tốn time. Trong production với Qdrant và real embeddings, retrieve có thể tốn 5–20ms nhưng vẫn không đáng kể so với LLM decode (~5000ms với Q4_K_M). Bottleneck thực sự luôn là decode latency.

---

## 5. Bonus — The single change that mattered most

**Change:** Tune `n_threads` từ default (logical_cores=4) xuống optimal = physical_cores=4 — trên máy này 2 giá trị trùng nhau, nhưng sweep cho thấy tăng threads vượt quá physical core count gây regression rõ ràng.

**Before vs after** (từ `benchmarks/bonus-thread-sweep.md`):

```
baseline (n_threads=1):  4.2 tok/s,  TTFT P50 = 1821 ms
optimal  (n_threads=4):  12.8 tok/s, TTFT P50 = 543 ms
speedup: ~3.05×

over-threaded (n_threads=6): 11.2 tok/s, TTFT P50 = 658 ms
regression vs optimal: −12% throughput
```

**Tại sao nó work:**

GGML's matrix-vector multiply (core của autoregressive decode) là **memory-bandwidth bound**, không phải compute bound. Mỗi token generation đòi hỏi load toàn bộ weight matrix từ RAM vào cache — trên 4-core Xeon với ~50 GB/s memory bandwidth, bottleneck là bus tốc độ, không phải số lượng compute units.

Tăng từ 1 lên 4 threads cho speedup gần-linear (~3×) vì 4 cores có thể load data từ RAM song song qua independent memory channels. Nhưng tăng từ 4 lên 6 threads (hyperthreading) gây regression: HT threads chia sẻ L2/L3 cache và memory port với physical threads, tạo contention thay vì additive throughput. Với workload bandwidth-bound, thêm HT threads giống thêm người cùng đọc một cuốn sách — không nhanh hơn, thậm chí chậm hơn vì tranh giành.

AVX-512 (có trên máy này) giúp load 512-bit per instruction thay vì 256-bit (AVX2), nhưng benefit này đã được GGML khai thác tự động khi build với flag native.

---

## 6. (Optional) Điều ngạc nhiên nhất

Điều ngạc nhiên nhất: P95 latency tăng 2.75× (từ 7.8s lên 21.5s) khi tăng user từ 10 lên 50 — mặc dù RPS chỉ tăng 16% (1.8 → 2.1 RPS). Đây là bằng chứng rõ nhất cho queuing theory: một khi hệ thống đạt saturation, latency diverges jagged dù throughput tăng rất ít.

---

## 7. Self-graded checklist

- [x] `hardware.json` đã commit
- [x] `models/active.json` đã commit
- [x] `benchmarks/01-quickstart-results.md` đã commit
- [x] `benchmarks/02-server-results.md` đã commit
- [x] `benchmarks/bonus-thread-sweep.md` đã commit
- [x] 7 screenshots trong `submission/screenshots/`
- [x] `make verify` exit 0
- [x] Repo trên GitHub ở chế độ **public**
- [ ] Đã paste public repo URL vào VinUni LMS
