import glob
import os
import time
import sys
from pathlib import Path
import rdflib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_TTL = PROJECT_ROOT / "src" / "mmdio" / "engine" / "registry.ttl"
ONTOLOGY_TTL = PROJECT_ROOT / "packs" / "mmdio-pack" / "ontology.ttl"
GATES_DIR = PROJECT_ROOT / "packs" / "mmdio-pack" / "gates"

t0 = time.time()
graph = rdflib.Graph()
print("Parsing TTL files...", flush=True)
graph.parse(str(REGISTRY_TTL), format="turtle")
graph.parse(str(ONTOLOGY_TTL), format="turtle")
print(f"Graph parsed in {time.time() - t0:.2f}s, total triples: {len(graph)}", flush=True)

gate_files = sorted(glob.glob(os.path.join(str(GATES_DIR), "*.rq")))
for gf in gate_files:
    t1 = time.time()
    with open(gf, "r", encoding="utf-8") as f:
        query_str = f.read()
    print(f"Running gate {os.path.basename(gf)}...", flush=True)
    results = list(graph.query(query_str))
    print(f"Gate {os.path.basename(gf)} evaluated in {time.time() - t1:.2f}s, violations: {len(results)}", flush=True)
