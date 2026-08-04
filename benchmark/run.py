"""Benchmark ARC against other formats using C. elegans connectome data.

Usage:
    python benchmark/run.py
"""

import csv
import json
import os
import struct
import tempfile
import time
from pathlib import Path

import numpy as np

NEURONS = 302
SYNAPSES = 7000
N_ROUNDS = 50


def make_celegans():
    np.random.seed(42)
    src = np.random.randint(0, NEURONS, size=SYNAPSES, dtype=np.uint32)
    dst = np.random.randint(0, NEURONS, size=SYNAPSES, dtype=np.uint32)
    weight = np.random.uniform(0.5, 10.0, size=SYNAPSES).astype(np.float16)
    return src, dst, weight


def bench_arc(src, dst, weight):
    from neurarc import ArcFile, save, load

    header = {
        "format_version": 1,
        "neuron_count": NEURONS,
        "neuron_model": "LIF",
        "synapse_count": SYNAPSES,
        "connectivity_format": "edge_list",
        "populations": {"neurons": {"n_neurons": NEURONS, "global_offset": 0}},
        "projections": {"chem": {"source": "neurons", "target": "neurons"}},
        "tensors": {
            "synapse_src": {"offset": 0, "length": SYNAPSES, "dtype": "u32"},
            "synapse_dst": {"offset": SYNAPSES * 4, "length": SYNAPSES, "dtype": "u32"},
            "synapse_weight": {"offset": SYNAPSES * 8, "length": SYNAPSES, "dtype": "f16"},
        },
    }
    arc = ArcFile(header=header, tensors={"synapse_src": src, "synapse_dst": dst, "synapse_weight": weight})

    path = tempfile.NamedTemporaryFile(suffix=".arc", delete=False).name
    save(path, arc)
    size = os.path.getsize(path)

    t0 = time.perf_counter()
    for _ in range(N_ROUNDS):
        load(path)
    read_ms = (time.perf_counter() - t0) / N_ROUNDS * 1000

    os.unlink(path)
    return size, read_ms


def bench_csv(src, dst, weight):
    lines = [f"{src[i]},{dst[i]},{weight[i]}" for i in range(SYNAPSES)]
    data = "\n".join(lines)

    path = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w").name
    with open(path, "w") as f:
        f.write(data)
    size = os.path.getsize(path)

    t0 = time.perf_counter()
    for _ in range(N_ROUNDS):
        rows = []
        with open(path) as f:
            for row in csv.reader(f):
                rows.append((int(row[0]), int(row[1]), float(row[2])))
    read_ms = (time.perf_counter() - t0) / N_ROUNDS * 1000

    os.unlink(path)
    return size, read_ms


def bench_json(src, dst, weight):
    data = json.dumps([[int(src[i]), int(dst[i]), float(weight[i])] for i in range(SYNAPSES)])

    path = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w").name
    with open(path, "w") as f:
        f.write(data)
    size = os.path.getsize(path)

    t0 = time.perf_counter()
    for _ in range(N_ROUNDS):
        with open(path) as f:
            json.load(f)
    read_ms = (time.perf_counter() - t0) / N_ROUNDS * 1000

    os.unlink(path)
    return size, read_ms


def bench_adj_matrix(src, dst, weight):
    adj = np.zeros((NEURONS, NEURONS), dtype=np.float32)
    for i in range(SYNAPSES):
        adj[src[i], dst[i]] = float(weight[i])

    path = tempfile.NamedTemporaryFile(suffix=".bin", delete=False).name
    adj.tofile(path)
    size = os.path.getsize(path)

    t0 = time.perf_counter()
    for _ in range(N_ROUNDS):
        np.fromfile(path, dtype=np.float32).reshape(NEURONS, NEURONS)
    read_ms = (time.perf_counter() - t0) / N_ROUNDS * 1000

    os.unlink(path)
    return size, read_ms


def bench_numpy_coo(src, dst, weight):
    coo = np.column_stack([src, dst, weight])

    path = tempfile.NamedTemporaryFile(suffix=".npy", delete=False).name
    np.save(path, coo)
    size = os.path.getsize(path)

    t0 = time.perf_counter()
    for _ in range(N_ROUNDS):
        np.load(path)
    read_ms = (time.perf_counter() - t0) / N_ROUNDS * 1000

    os.unlink(path)
    return size, read_ms


def main():
    src, dst, weight = make_celegans()

    benchmarks = [
        ("ARC (edge_list)", bench_arc),
        ("CSV", bench_csv),
        ("JSON array", bench_json),
        ("Adj matrix (bin)", bench_adj_matrix),
        ("NumPy COO (.npy)", bench_numpy_coo),
    ]

    print(f"{'Format':<20} {'Size':>10} {'Read':>10} {'B/syn':>8}")
    print("-" * 52)

    results = []
    for name, fn in benchmarks:
        size, read_ms = fn(src, dst, weight)
        bpsyn = size / SYNAPSES
        print(f"{name:<20} {size:>8,} B {read_ms:>8.2f} ms {bpsyn:>6.1f}")
        results.append((name, size, read_ms, bpsyn))

    print(f"\n{NEURONS} neurons, {SYNAPSES:,} synapses, {N_ROUNDS} rounds")

    # relative comparison
    arc_size = results[0][1]
    print("\nRelative to ARC:")
    for name, size, read_ms, bpsyn in results:
        print(f"  {name:<20} {size/arc_size:.1f}x size")


if __name__ == "__main__":
    main()
