# ARC Benchmark

Compare ARC against common neural data formats on size and read speed.

## Setup

```bash
pip install neurarc numpy
```

## Run

```bash
python benchmark/run.py
```

## Results

C. elegans connectome (302 neurons, 7,000 synapses):

```
Format                 Size       Read    B/syn
----------------------------------------------------
ARC (edge_list)     70,440 B     0.34 ms   10.1
CSV                130,387 B    13.82 ms   18.6
JSON array         158,389 B     5.25 ms   22.6
Adj matrix (bin)   364,816 B     0.39 ms   52.1
NumPy COO (.npy)   168,128 B     0.67 ms   24.0
```

ARC is the smallest and fastest format for connectivity data.

### Projected sizes at scale

| Synapses | ARC edge list | CSR | CSV | JSON |
|----------|--------------|-----|-----|------|
| 10K | 100 KB | 60 KB | 190 KB | 230 KB |
| 1M | 10 MB | 6 MB | 19 MB | 23 MB |
| 100M | 1 GB | 600 MB | 19 GB | 23 GB |
| 1B | 10 GB | 6 GB | 190 GB | 230 GB |
