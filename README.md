# neurarc

A compact binary file format for encoding neural connectome data.

## What is ARC?

**ARC** (version 1) is a binary format designed to store neural connectivity data in a compact, machine-readable way. It encodes:

- **Neuron populations** — named groups with counts, offsets, and model parameters
- **Synaptic connectivity** — source/destination indices and weights
- **Neuron model parameters** — membrane time constants, thresholds, reset voltages (LIF model)
- **I/O port mappings** — named input/output ports for external interaction

The format separates human-readable metadata (JSON header) from packed binary data (tensor blob), making it both inspectable and efficient.

## Why?

Neural connectome data — complete maps of synaptic connections in nervous systems — is central to computational neuroscience and neuromorphic engineering. Existing formats tend to be either human-readable but bulky (JSON, XML) or fast but opaque (custom binaries with no self-description).

ARC splits the difference: a small JSON header carries all the metadata you need to interpret the file, while the actual connectivity data is packed into typed binary arrays with minimal overhead.

## File Format

```
┌───────────────┬──────────────┬─────────────────┬──────────────┐
│  Magic (4 B)  │ Header Len   │  Header JSON    │  Binary Blob │
│               │  (8 B, LE)   │  (UTF-8)        │              │
└───────────────┴──────────────┴─────────────────┴──────────────┘
```

1. **Magic bytes** — `ARC1` (4 bytes)
2. **Header length** — unsigned 64-bit little-endian integer
3. **Header** — JSON object with all metadata (populations, projections, tensor descriptors)
4. **Blob** — packed binary arrays (neuron indices, synaptic weights, etc.)

## Connectivity Encoding

Two sparse matrix encodings are supported:

- **Edge list** — parallel arrays of source indices, destination indices, and weights
- **CSR** (Compressed Sparse Row) — row pointers + column indices + weights

## Data Types

| Type | Size | Use |
|------|------|-----|
| `u8` | 1 byte | Flags, booleans |
| `u32` | 4 bytes | Neuron indices |
| `f16` | 2 bytes | Synaptic weights (half-precision) |
| `f32` | 4 bytes | Weights when higher precision is needed |

All values are little-endian.

## Example (Python)

```python
import json, struct, numpy as np

with open("network.arc", "rb") as f:
    magic = f.read(4)                         # b"ARC1"
    header_len = struct.unpack("<Q", f.read(8))[0]
    header = json.loads(f.read(header_len))
    blob = f.read()

def read_tensor(name):
    t = header["tensors"][name]
    dt = {"u8": np.uint8, "u32": np.uint32,
          "f16": np.float16, "f32": np.float32}[t["dtype"]]
    return np.frombuffer(blob, dtype=dt,
                         count=t["length"], offset=t["offset"])

src    = read_tensor("synapse_src")
dst    = read_tensor("synapse_dst")
weight = read_tensor("synapse_weight")
```

## Specification

See [ARC_SPEC.md](ARC_SPEC.md) for the full format specification, including the JSON schema, tensor layout, and I/O map structure.

## License

TBD
