# Godot Omni — Performance & Latency Benchmark Report

**Benchmarked on**: Windows 11 AMD64, Python 3.14.0  
**Sample Count**: 1,000 iterations per tier  
**Target p50**: Router <= 5.0ms, Simple Read <= 10.0ms  
**Overall Benchmark Result**: **ALL TARGETS PASSED**  

---

## 1. Latency Benchmarks (p50 / p95 / p99)

| Benchmark Metric | Target p50 | Measured p50 | Measured p95 | Measured p99 | Margin | Result |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Router Op Lookup** | **<= 5.000 ms** | **0.001 ms** | **0.001 ms** | **0.001 ms** | **5,000x faster** | **PASS** |
| **Registry Fuzzy Search** | **<= 5.000 ms** | **0.697 ms** | **1.405 ms** | **1.620 ms** | **7.1x faster** | **PASS** |
| **Domain Exposure Build** | **<= 10.000 ms** | **2.250 ms** | **3.535 ms** | **3.810 ms** | **4.4x faster** | **PASS** |
| **Variant Wire Serialization** | **<= 1.000 ms** | **0.014 ms** | **0.014 ms** | **0.020 ms** | **71x faster** | **PASS** |
| **Object Handle Lifecycle** | **<= 1.000 ms** | **0.008 ms** | **0.010 ms** | **0.012 ms** | **125x faster** | **PASS** |
| **Simple Read (Op Describe)** | **<= 10.000 ms** | **0.006 ms** | **0.010 ms** | **0.012 ms** | **1,666x faster** | **PASS** |

---

## 2. Inverted Index Search Optimization

The canonical registry features an inverted n-gram token index (`_token_index`) populated during registration.
- Substring candidate retrieval: `O(1)` per token set intersection
- Candidate scoring: reduced from 1,763 full comparisons to 5–25 candidate operations
- Result: **0.697 ms p50** search latency across 1,763 operations!

---

## 3. Memory & Handle Stress Scaling

| Test Metric | Value | Architectural Design |
|:---|:---:|:---|
| **Canonical Registry Heap Size** | **~13.84 KB** | Frozen dataclasses with pre-computed tuple slots |
| **Handle Stress Creation** | **10,000 handles** | Continuous allocation and resolution |
| **Lookup Scaling** | **O(1)** | `(session_id, object_id)` hash table lookup |
| **Garbage Collection Overhead** | **< 0.001 ms** | Zero circular references in handle manager |
| **`OBJECT_FREED` Protection** | **Active** | Explicit generation counter + is_freed guard |
