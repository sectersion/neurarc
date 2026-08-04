# neurarc

The fastest binary format for neural connectome data.

## What is ARC?

**ARC** (version 1) is a compact binary format for storing neural connectivity data:

- **Neuron populations** — named groups with counts, offsets, and model parameters
- **Synaptic connectivity** — source/destination indices and weights
- **Neuron model parameters** — membrane time constants, thresholds, reset voltages
- **I/O port mappings** — named input/output ports for external interaction

## Performance

ARC is the smallest and fastest format for connectivity data.

```
Format                 Size       Read    B/syn
----------------------------------------------------
ARC (edge_list)     70,440 B     0.34 ms   10.1
CSV                130,387 B    13.82 ms   18.6
JSON array         158,389 B     5.25 ms   22.6
Adj matrix (bin)   364,816 B     0.39 ms   52.1
NumPy COO (.npy)   168,128 B     0.67 ms   24.0
```

Benchmarked on C. elegans (302 neurons, 7,000 synapses). See [benchmark/](benchmark/) for code and projected sizes at scale.

| Metric | ARC | CSV | JSON |
|--------|-----|-----|------|
| Size | 10 B/synapse | 19 B/synapse | 23 B/synapse |
| Read | 0.34 ms | 13.8 ms | 5.3 ms |
| Format overhead | 12 bytes | per-line | per-element |

At 100M synapses: ARC = **1 GB**, CSV = **19 GB**, JSON = **23 GB**.

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

## License

MIT
