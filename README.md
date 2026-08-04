# neurarc

A compact binary file format for encoding neural connectome data.

## What is ARC?

**ARC** (version 1) is a binary format for storing neural connectivity data. It encodes:

- **Neuron populations** — named groups with counts, offsets, and model parameters
- **Synaptic connectivity** — source/destination indices and weights
- **Neuron model parameters** — membrane time constants, thresholds, reset voltages
- **I/O port mappings** — named input/output ports for external interaction

The format separates metadata (JSON header) from packed binary data (tensor blob), making it both inspectable and efficient.

## Why?

Neural connectome data — complete maps of synaptic connections in nervous systems — is central to computational neuroscience and neuromorphic engineering. Existing formats tend to be either human-readable but bulky (JSON, XML) or fast but opaque.

ARC splits the difference: a small JSON header carries all the metadata needed to interpret the file, while the actual connectivity data is packed into typed binary arrays with minimal overhead.

## Format Overview

```
┌───────────────┬──────────────┬─────────────────┬──────────────┐
│  Magic (4 B)  │ Header Len   │  Header JSON    │  Binary Blob │
│               │  (8 B, LE)   │  (UTF-8)        │              │
└───────────────┴──────────────┴─────────────────┴──────────────┘
```

- **Magic bytes** — `ARC1`
- **Header length** — u64 little-endian
- **Header** — JSON with populations, projections, tensor descriptors
- **Blob** — packed binary arrays

Supports edge list and CSR sparse matrix encodings. Data types: `u8`, `u32`, `f16`, `f32` (all little-endian).

## Specification

See [ARC_SPEC.md](ARC_SPEC.md) for the full format specification.

## License

TBD
