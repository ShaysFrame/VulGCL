"""PDG extraction: C function string → networkx DiGraph via Joern."""

import html
import os
import re
import subprocess
import tempfile
import textwrap
import networkx as nx


JOERN_WORKSPACE = os.path.expanduser("~/Dev/research/workspace")
os.makedirs(JOERN_WORKSPACE, exist_ok=True)

# Regex patterns for Joern's DOT output
_NODE_RE = re.compile(
    r'"(\d+)"\s+\[label\s*=\s*<([^,<>]+),\s*(\d+)<BR/>([^>]*)>\s*\]'
)
_EDGE_RE = re.compile(
    r'"(\d+)"\s*->\s*"(\d+)"\s*\[\s*label\s*=\s*"DDG:\s*([^"]*)"\s*\]'
)


def extract_pdg(c_code: str, project_name: str = "tmp_func") -> nx.DiGraph:
    """
    Given a C function as a string, run Joern and return its PDG as a DiGraph.

    Node attributes : type (str), line (int), code (str)
    Edge attributes : var  (str)  — variable carrying the dependency
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        c_file = os.path.join(tmpdir, "func.c")
        sc_file = os.path.join(tmpdir, "extract.sc")

        with open(c_file, "w") as f:
            f.write(c_code)

        # Joern script: import → query only non-stub methods → exit
        # isNotStub excludes built-in stubs like strcpy, <operator>, <global>
        script = textwrap.dedent(f"""
            importCode("{c_file}", "{project_name}")
            val pdgs = cpg.method.isNotStub.dotPdg.l
            pdgs.foreach(println)
            exit
        """).strip()
        with open(sc_file, "w") as f:
            f.write(script)

        result = subprocess.run(
            ["joern", "--script", sc_file],
            capture_output=True,
            text=True,
            timeout=180,
        )

    return _parse_dot(result.stdout)


def _parse_dot(dot_text: str) -> nx.DiGraph:
    """
    Parse Joern's DOT output. Handles multiple digraph blocks by returning
    the one with the most nodes (= the user's function, not stubs).
    """
    # Split into individual digraph "name" { ... } blocks
    blocks = re.split(r'(?=digraph\s+")', dot_text)

    best = nx.DiGraph()
    for block in blocks:
        if "digraph" not in block:
            continue
        G = nx.DiGraph()
        for m in _NODE_RE.finditer(block):
            nid = m.group(1)
            ntype = html.unescape(m.group(2)).strip()
            line = int(m.group(3))
            code = html.unescape(m.group(4)).strip()
            G.add_node(nid, type=ntype, line=line, code=code)
        for m in _EDGE_RE.finditer(block):
            src, dst, var = m.group(1), m.group(2), m.group(3).strip()
            # Only add edges between nodes we actually parsed (avoid bare nodes)
            if src in G and dst in G:
                G.add_edge(src, dst, var=var)
        if G.number_of_nodes() > best.number_of_nodes():
            best = G

    return best


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
