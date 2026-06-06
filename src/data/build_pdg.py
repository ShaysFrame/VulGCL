"""PDG extraction: C function string → networkx DiGraph via Joern."""

import html
import os
import re
import subprocess
import tempfile
import networkx as nx


# Joern v2.0.406 DOT format:
#   node: "8" [label = <(METHOD,foo)<SUB>1</SUB>> ]
#   stub: "46" [label = <(METHOD,strlen)> ]        (no <SUB> line number)
#   edge: "13" -> "20"  [ label = "DDG: x"]
_NODE_RE = re.compile(
    r'"(\d+)"\s*\[label\s*=\s*<\(([^,]+),(.+?)\)(?:<SUB>(\d+)</SUB>)?>\s*\]'
)
_EDGE_RE = re.compile(
    r'"(\d+)"\s*->\s*"(\d+)"\s*\[\s*label\s*=\s*"DDG:\s*([^"]*)"\s*\]'
)


def extract_pdg(c_code: str, project_name: str = "tmp_func") -> nx.DiGraph:
    """
    Given a C function as a string, run Joern and return its PDG as a DiGraph.

    Uses joern-parse + joern-export (Joern v2.x API).
    Node attributes : type (str), line (int), code (str)
    Edge attributes : var  (str)  — variable carrying the dependency
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        c_file  = os.path.join(tmpdir, "func.c")
        cpg_file = os.path.join(tmpdir, "cpg.bin")
        out_dir  = os.path.join(tmpdir, "pdg_out")  # joern-export creates this

        with open(c_file, "w") as f:
            f.write(c_code)

        # Step 1: parse C file → CPG binary
        r1 = subprocess.run(
            ["joern-parse", c_file, "--output", cpg_file],
            capture_output=True, text=True, timeout=180,
        )
        if r1.returncode != 0 or not os.path.exists(cpg_file):
            return nx.DiGraph()

        # Step 2: export PDG as DOT files (one file per method)
        r2 = subprocess.run(
            ["joern-export", "--repr", "pdg", "--out", out_dir, cpg_file],
            capture_output=True, text=True, timeout=180,
        )
        if not os.path.exists(out_dir):
            return nx.DiGraph()

        # Step 3: parse all DOT files, return the largest user-code graph
        # User functions have <SUB>line</SUB> tags; stubs do not
        best = nx.DiGraph()
        for fname in os.listdir(out_dir):
            if not fname.endswith(".dot"):
                continue
            with open(os.path.join(out_dir, fname)) as f:
                dot_text = f.read()
            G = _parse_dot_file(dot_text)
            has_lines     = any(G.nodes[n].get("line", 0) > 0 for n in G.nodes)
            best_has_lines = any(best.nodes[n].get("line", 0) > 0 for n in best.nodes)
            if has_lines and (not best_has_lines or G.number_of_nodes() > best.number_of_nodes()):
                best = G

    return best


def _parse_dot_file(dot_text: str) -> nx.DiGraph:
    G = nx.DiGraph()
    for m in _NODE_RE.finditer(dot_text):
        nid   = m.group(1)
        ntype = html.unescape(m.group(2)).strip()
        code  = html.unescape(m.group(3)).strip()
        line  = int(m.group(4)) if m.group(4) else 0
        G.add_node(nid, type=ntype, line=line, code=code)
    for m in _EDGE_RE.finditer(dot_text):
        src, dst, var = m.group(1), m.group(2), m.group(3).strip()
        if src in G and dst in G:
            G.add_edge(src, dst, var=var)
    return G


# Alias for backwards compatibility
def _parse_dot(dot_text: str) -> nx.DiGraph:
    return _parse_dot_file(dot_text)


if __name__ == "__main__":
    VULNERABLE = """
void copy_input(char *user_input) {
    char buf[64];
    strcpy(buf, user_input);
}
"""

    print("Extracting PDG for vulnerable function...")
    G = extract_pdg(VULNERABLE, project_name="test_vuln")

    print(f"\nNodes ({G.number_of_nodes()}):")
    for nid, attr in G.nodes(data=True):
        print(f"  [{attr['type']:25s}] line={attr['line']}  code={attr['code']!r}")

    print(f"\nEdges ({G.number_of_edges()}) — data dependencies:")
    for src, dst, attr in G.edges(data=True):
        src_code = G.nodes[src].get("code", src)
        dst_code = G.nodes[dst].get("code", dst)
        print(f"  {src_code!r:30s} --DDG:{attr['var']!r}--> {dst_code!r}")

    print(f"\nSummary:")
    print(f"  Nodes : {G.number_of_nodes()}")
    print(f"  Edges : {G.number_of_edges()}")
    print(f"  Is DAG: {nx.is_directed_acyclic_graph(G)}")
