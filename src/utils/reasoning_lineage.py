import networkx as nx
import matplotlib.pyplot as plt


def get_reasoning_trace(results, criterion_name: str):
    for r in results:
        if r.get("criterion") == criterion_name:
            return r.get("reasoning_trace")
    raise ValueError(f"Criterion '{criterion_name}' not found in results.")

def build_reasoning_graph(trace):
    G = nx.DiGraph()

    # Add ToT thoughts
    for i, thought in enumerate(trace.get("tot_thoughts", [])):
        node_id = f"tot_{i}"
        G.add_node(node_id, label=f"ToT: {thought['text']}", type="thought", source="ToT")
    
    # Add ReAct steps
    for i, step in enumerate(trace.get("react_steps", [])):
        t_id = f"react_{i}_thought"
        a_id = f"react_{i}_action"
        o_id = f"react_{i}_obs"

        G.add_node(t_id, label=f"ReAct: {step['thought']}", type="thought", source="ReAct")
        G.add_node(a_id, label=f"Action: {step['action']}", type="action")
        G.add_node(o_id, label=f"Obs: {step['observation'][:100]}...", type="observation")

        # Chain them: thought → action → observation
        G.add_edge(t_id, a_id)
        G.add_edge(a_id, o_id)

        # Optionally link ToT thoughts to ReAct (can be smarter later)
        for j in range(len(trace.get("tot_thoughts", []))):
            G.add_edge(f"tot_{j}", t_id)

    # Final Score Node
    score_node = "final_score"
    G.add_node(score_node, label=f"Final Score: {trace['score']} – {trace['score_explanation'][:80]}...", type="score")

    # Link all observations to score
    for i in range(len(trace.get("react_steps", []))):
        G.add_edge(f"react_{i}_obs", score_node)

    return G




def draw_reasoning_graph(G, figsize=(14, 10), title="Reasoning Lineage Graph"):
    pos = nx.spring_layout(G, seed=42, k=0.7)

    # Group nodes by type
    node_colors = []
    node_labels = {}
    for n, data in G.nodes(data=True):
        node_labels[n] = data.get("label", n)
        t = data.get("type")
        if t == "thought" and data.get("source") == "ToT":
            node_colors.append("skyblue")
        elif t == "thought" and data.get("source") == "ReAct":
            node_colors.append("lightgreen")
        elif t == "action":
            node_colors.append("orange")
        elif t == "observation":
            node_colors.append("gray")
        elif t == "score":
            node_colors.append("gold")
        else:
            node_colors.append("lightgray")

    plt.figure(figsize=figsize)
    nx.draw(
        G, pos,
        with_labels=True,
        labels=node_labels,
        node_color=node_colors,
        node_size=2000,
        font_size=8,
        edge_color="black",
        arrows=True
    )
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()
