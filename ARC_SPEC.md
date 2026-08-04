# ARC v1 — Binary Connectome Format

**Version:** 1  
**Date:** 2026-08-01

## 1. File Layout

```
┌───────────────┬──────────────┬─────────────────┬──────────────┐
│  Magic (4 B)  │ Header Len   │  Header JSON    │  Binary Blob │
│               │  (8 B, LE)   │  (UTF-8)        │              │
└───────────────┴──────────────┴─────────────────┴──────────────┘
```

| Offset | Size | Type | Field | Description |
|--------|------|------|-------|-------------|
| 0 | 4 | bytes | magic | `0x41 0x52 0x43 0x31` — the ASCII string `ARC1` |
| 4 | 8 | u64 LE | header_len | Byte length of the JSON header that follows |
| 12 | header_len | UTF-8 | header | JSON object (see §2) |
| 12 + header_len | variable | bytes | blob | Packed tensor data (see §3) |

All multi-byte integers are **little-endian**.

---

## 2. Header JSON

The header is a single JSON object encoded as UTF-8. It contains all metadata
needed to interpret the binary blob. Fields marked **(R)** are required; all
others are optional with the noted defaults.

### 2.1 Top-Level Fields

| Field | Type | Req | Description |
|-------|------|-----|-------------|
| `format_version` | integer | **R** | Must be `1` for this spec. |
| `neuron_count` | integer | **R** | Total number of neurons across all populations. |
| `neuron_model` | string | **R** | Neuron model name (e.g. `"LIF"`). Informational; the simulator decides how to interpret parameters. |
| `neuron_params` | object | — | Default neuron parameters (see §2.2). Omitted when per-population params are used. |
| `synapse_count` | integer | **R** | Total number of synapses (edges) across all projections. |
| `connectivity_format` | string | **R** | How synapses are encoded in the blob: `"edge_list"` (default) or `"csr"` (see §3.2). |
| `populations` | object | — | Named neuron groups (see §2.3). |
| `projections` | object | — | Named synaptic pathways (see §2.4). |
| `io_map` | object | — | Input/output port declarations (see §2.5). |
| `tensors` | object | **R** | Descriptions of every tensor in the binary blob (see §3). |

### 2.2 `neuron_params` (Default / Fallback)

Used when all populations share the same parameters, or when `populations` is
omitted. Parameters use **SI-derived units** stored as plain floats.

| Field | Unit suffix | Default | Description |
|-------|-------------|---------|-------------|
| `tau_ms` | milliseconds | 10.0 | Membrane time constant |
| `v_thresh_mv` | millivolts | -50.0 | Spike threshold |
| `v_reset_mv` | millivolts | -70.0 | Reset potential |
| `v_rest_mv` | millivolts | -70.0 | Resting potential |

### 2.3 `populations`

A JSON object keyed by population name. Each value:

| Field | Type | Req | Description |
|-------|------|-----|-------------|
| `n_neurons` | integer | **R** | Number of neurons in this population. |
| `global_offset` | integer | **R** | Index of this population's first neuron in the global (flattened) neuron array. Populations must not overlap. |
| `tau_ms` | float | — | Time constant (overrides `neuron_params`). |
| `v_thresh_mv` | float | — | Threshold voltage. |
| `v_reset_mv` | float | — | Reset voltage. |
| `v_rest_mv` | float | — | Resting voltage. |

**Example:**
```json
"populations": {
  "sensory": { "n_neurons": 80, "global_offset": 0, "v_thresh_mv": -45.0 },
  "motor":   { "n_neurons": 50, "global_offset": 80 }
}
```

### 2.4 `projections`

A JSON object keyed by projection name. Each value:

| Field | Type | Req | Description |
|-------|------|-----|-------------|
| `source` | string | **R** | Name of the presynaptic population (must exist in `populations`). |
| `target` | string | **R** | Name of the postsynaptic population. |

Synapses for each projection are stored in the blob; they are **not** grouped
by projection in the tensors — instead, all synapses are packed contiguously and
the reader assigns edges to projections using the `source`/`target` population
names plus `global_offset` / `n_neurons` to map global indices back to local
ones.

### 2.5 `io_map`

Named I/O ports for external interaction. Structure:

```json
"io_map": {
  "inputs": [
    {
      "name": "touch",
      "population": "sensory",
      "neuron_ids": [0, 3, 7],
      "encoding": "direct_current"
    }
  ],
  "outputs": [
    {
      "name": "command",
      "population": "motor",
      "neuron_ids": [10, 11, 12, 13],
      "decoding": "rate"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Port name (unique within inputs or outputs). |
| `population` | string | Population containing these neurons. |
| `neuron_ids` | integer[] | Indices **within** the named population (not global). |
| `encoding` | string | Input encoding scheme (e.g. `"direct_current"`). Informational. |
| `decoding` | string | Output decoding scheme (e.g. `"rate"`). Informational. |

---

## 3. Binary Blob — Tensors

The blob begins immediately after the header JSON at byte offset `12 + header_len`.
It contains packed arrays described by the `tensors` object in the header.

### 3.1 Tensor Descriptor

Each entry in `tensors`:

| Field | Type | Description |
|-------|------|-------------|
| `offset` | integer | **Byte offset** from the start of the blob to the first byte of this tensor. |
| `length` | integer | Number of elements in the tensor. |
| `dtype` | string | Element type (see §3.3). |

**Byte offset of a tensor = `12 + header_len + descriptor.offset`.**

### 3.2 Required Tensors

#### `edge_list` format (default)

Three parallel arrays, all of length `synapse_count`:

| Tensor | dtype | Description |
|--------|-------|-------------|
| `synapse_src` | `u32` | Global index of the presynaptic neuron. |
| `synapse_dst` | `u32` | Global index of the postsynaptic neuron. |
| `synapse_weight` | `f16` | Synaptic weight (in mV). |

Neuron *i* in population *P* has global index `P.global_offset + i`.

#### `csr` format (Compressed Sparse Row)

| Tensor | dtype | Description |
|--------|-------|-------------|
| `synapse_row_ptr` | `u32` | Row pointers. Length = `neuron_count + 1`. `row_ptr[i]` to `row_ptr[i+1]` defines the range of outgoing edges for neuron *i*. |
| `synapse_col_idx` | `u32` | Column (target) indices. Length = `synapse_count`. |
| `synapse_weight` | `f16` | Synaptic weights. Length = `synapse_count`. |

### 3.3 Supported dtypes

| String | C type | Bytes | Notes |
|--------|--------|-------|-------|
| `"u8"` | `uint8_t` | 1 | Flags, booleans, small enums |
| `"u32"` | `uint32_t` | 4 | Neuron indices, row pointers |
| `"f16"` | `float16` | 2 | Weights (IEEE 754 half-precision) |
| `"f32"` | `float32` | 4 | Weights when higher precision is needed |

All values are stored in **little-endian** byte order.

### 3.4 Additional / Future Tensors

Implementations may include extra tensors (e.g. `synapse_delay`, `synapse_type`)
by adding entries to `tensors`. Unknown keys should be ignored by readers.

---

## 4. Walkthrough — Reading an ARC File

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

src    = read_tensor("synapse_src")     # uint32, [synapse_count]
dst    = read_tensor("synapse_dst")     # uint32, [synapse_count]
weight = read_tensor("synapse_weight")  # float16, [synapse_count]
```

---

## 5. Walkthrough — Writing an ARC File

```python
import json, struct, numpy as np

# ... build src, dst, weight arrays ...
src    = np.asarray(src, dtype=np.uint32)
dst    = np.asarray(dst, dtype=np.uint32)
weight = np.asarray(weight, dtype=np.float16)
n = len(src)

offsets = {}
off = 0
for name, arr in [("synapse_src", src), ("synapse_dst", dst),
                  ("synapse_weight", weight)]:
    offsets[name] = {"offset": off, "length": len(arr),
                     "dtype": {np.uint8: "u8", np.uint32: "u32",
                               np.float16: "f16", np.float32: "f32"}[arr.dtype]}
    off += arr.nbytes

header = {
    "format_version": 1,
    "neuron_count": neuron_count,
    "neuron_model": "LIF",
    "synapse_count": n,
    "connectivity_format": "edge_list",
    "populations": { ... },
    "projections": { ... },
    "io_map": { ... },
    "tensors": offsets,
}

header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")

with open("network.arc", "wb") as f:
    f.write(b"ARC1")
    f.write(struct.pack("<Q", len(header_bytes)))
    f.write(header_bytes)
    f.write(src.tobytes())
    f.write(dst.tobytes())
    f.write(weight.tobytes())
```

---

*End of ARC v1 specification.*
