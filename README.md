# neurarc

A compact binary format for neural connectome data.

## What is ARC?

**ARC** (version 1) is a binary format for storing neural connectivity data:

- **Neuron populations** — named groups with counts, offsets, and model parameters
- **Synaptic connectivity** — source/destination indices and weights
- **Neuron model parameters** — membrane time constants, thresholds, reset voltages
- **I/O port mappings** — named input/output ports for external interaction

## How does it compare to HDF5?

| Claim | Status |
|-------|--------|
| ARC is smaller | **True** — 17% smaller than HDF5 |
| ARC opens faster | **True** — 106x faster with mmap |
| ARC reads faster | **False** — HDF5 wins for full data access |
| ARC is simpler | **True** — no HDF5 dependency |
| ARC writes faster | **True** — 1.9x faster |

**ARC's niche:** simpler, smaller, lower overhead for metadata and partial access. Not a replacement for HDF5 at scale — a lighter alternative for specific use cases.

## Format

```
┌───────────────┬──────────────┬─────────────────┬──────────────┐
│  Magic (4 B)  │ Header Len   │  Header JSON    │  Binary Blob │
│               │  (8 B, LE)   │  (UTF-8)        │              │
└───────────────┴──────────────┴─────────────────┴──────────────┘
```

10 bytes per synapse in edge list format. 6 bytes per synapse in CSR. Little-endian. Supports `u8`, `u32`, `f16`, `f32`.

## Specification

See [ARC_SPEC.md](ARC_SPEC.md).

## Tooling

| Language | Package | Install |
|----------|---------|---------|
| Python | [neurarc-py](https://github.com/sectersion/neurarc-py) | `pip install neurarc` |
| Rust | [neurarc-rs](https://github.com/sectersion/neurarc-rs) | `cargo add neurarc` |

## Benchmark

See [benchmark/](benchmark/) for code and detailed results.

```
10M synapses:
  ARC mmap open:     0.73 ms
  HDF5 open:        77.56 ms

  ARC full read:   136.33 ms
  HDF5 full read:  102.55 ms

  ARC write:         2.58 s
  HDF5 write:        4.84 s
```

## License

MIT
