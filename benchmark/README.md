# ARC Benchmark

Compare ARC against HDF5 on connectivity data.

## Setup

```bash
pip install neurarc numpy h5py
```

## Run

```bash
python benchmark/run.py
```

## Results — C. elegans (283 neurons, 6,264 synapses)

```
Format                 Size       Read     B/syn
----------------------------------------------------
ARC (mmap)          70,315 B     1.64 ms   10.0
ARC (standard)      70,315 B     2.37 ms   10.0
HDF5 (flat)         86,048 B     8.36 ms   12.3
HDF5 (gzip)         48,479 B     3.35 ms    6.9
```

## Results — 10M synapses (fair comparison)

### File size

| Format | Size | Bytes/synapse |
|--------|------|---------------|
| **ARC** | **100 MB** | **10.0** |
| HDF5 | 120 MB | 12.0 |

ARC is 17% smaller than HDF5.

### Open time (header + setup)

| Method | Time |
|--------|------|
| **ARC mmap** | **0.73 ms** |
| HDF5 standard | 77.56 ms |

ARC mmap opens 106x faster (deferred data loading).

### Full read (load + access all data)

| Method | Time |
|--------|------|
| HDF5 standard | **102.55 ms** |
| ARC mmap | 136.33 ms |

HDF5 is faster for full data access (better internal caching/chunking).

### Write time

| Format | Time |
|--------|------|
| **ARC** | **2.58 s** |
| HDF5 | 4.84 s |

ARC writes 1.9x faster.

## What this means

| Claim | Status |
|-------|--------|
| ARC is smaller | **True** — 17% smaller |
| ARC opens faster | **True** — 106x faster (mmap) |
| ARC reads faster | **False** — HDF5 wins for full reads |
| ARC is simpler | **True** — no HDF5 dependency |
| ARC writes faster | **True** — 1.9x faster |

## When to use ARC

- Simplicity matters (no HDF5 dependency)
- Lower overhead for metadata/partial access
- Write-heavy workloads
- Embedded/resource-constrained environments

## When to use HDF5/SONATA

- Full data access performance matters
- Existing tooling ecosystem is needed
- Compression is important
- Large-scale simulation (SONATA format)
