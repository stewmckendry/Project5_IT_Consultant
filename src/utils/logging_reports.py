from pathlib import Path
from datetime import datetime
from matplotlib import pyplot as plt
import shutil
import json
from src.utils.logging_utils import openai_call_log, thought_dedup_stats
from src.utils.thought_filtering import get_embedding_cache_stats
import os
from src.utils.logging_utils import (
    log_phase,
    tool_stats,
    thought_score_stats,
    tool_failure,
    tool_failure_stats,
    openai_call_counter,
    openai_call_sources,
    openai_prompt_token_usage_by_source,
    openai_completion_token_usage_by_source,
    calculate_token_usage_summary,
    get_openai_call_avg_time)
from src.utils.export_utils import convert_markdown_to_html_and_pdf_rfp

def finalize_evaluation_run(output_dir="../outputs/proposal_eval_reports", run_id=None, results=None):
    log_phase("📊 Generating Logging Summary Report...")
    run_id = run_id or datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    img_dir = output_dir / "plots"
    img_dir.mkdir(exist_ok=True)

    # === Generate the content ===
    summary_lines = []
    summary_lines.append(f"# 📊 Evaluation Summary Report – `{run_id}`\n")

    # --- TOOL USAGE ---
    summary_lines.append("## 🔧 Tool Usage")
    for tool, count in tool_stats.items():
        summary_lines.append(f"- {tool}: {count} time(s)")
    _plot_bar(tool_stats, img_dir / "tool_usage.png", "Tool Usage")
    summary_lines.append("![Tool Usage](plots/tool_usage.png)\n")

    # --- THOUGHT SCORE DIST ---
    summary_lines.append("## 💭 Thought Score Distribution")
    for score, count in sorted(thought_score_stats.items(), reverse=True):
        summary_lines.append(f"- Score {score}: {count} thought(s)")
    _plot_bar(thought_score_stats, img_dir / "thought_scores.png", "Thought Scores")
    summary_lines.append("![Thought Scores](plots/thought_scores.png)\n")

    # --- ERRORS ---
    log_path = output_dir / "log_file.log"
    summary_lines.append(generate_log_health_md(log_path))

    # --- FAILURES ---
    summary_lines.append("## ❗ Tool Failures")
    for tool, reason in tool_failure.items():
        summary_lines.append(f"- {tool}: {reason}")
    summary_lines.append("\n---\n")
    
    # --- TOOL SUCCESS RATES ---
    summary_lines.append("## ✅ Tool Success Rates")
    for tool, total in tool_stats.items():
        fail = tool_failure_stats.get(tool, 0)
        success = total - fail
        rate = (success / total) * 100 if total else 0
        summary_lines.append(f"- {tool}: {success}/{total} successful ({rate:.1f}%)")
    summary_lines.append("\n---\n")

    # --- THOUGHTS ---
    summary_lines.append("## 🧠 Thoughts Generated")
    summary_lines.append(generate_thought_summary_md(results))
    summary_lines.append("\n---\n")

    # --- THOUGHT DEDUPLICATION ---
    summary_lines.append(get_thought_deduplication_summary_md())
    summary_lines.append("\n---\n")

    # --- EMBEDDING CACHE ---
    summary_lines.append(generate_embedding_cache_md())
    summary_lines.append("\n---\n")

    # --- REASONING TRACE BY CRITERION ---
    summary_lines.append("\n## 🧠 Reasoning Chain Analysis")
    summary_lines.append(generate_reasoning_trace_md(results))
    summary_lines.append("\n---\n")
    # === Reasoning Lineage Table ===
    summary_lines.append("\n## 🧠 Reasoning Lineage Table (All Criteria)\n")
    summary_lines.append(generate_reasoning_lineage_table_md(results))
    summary_lines.append("\n---\n")
    
    # --- OPENAI CALLS ---
    summary_lines.append("## 🔄 OpenAI API Calls")
    summary_lines.append(f"- Total Calls: {openai_call_counter}")
    avg_time = get_openai_call_avg_time()
    summary_lines.append(f"- Average Time: {avg_time:.2f} sec")
    summary_lines.append("\n---\n")
    summary_lines.append(f"- OpenAI Call Sources & Token Usage")
    for src, count in openai_call_sources.items():
        prompt_tokens = openai_prompt_token_usage_by_source.get(src, 0)
        completion_tokens = openai_completion_token_usage_by_source.get(src, 0)
        total_tokens = prompt_tokens + completion_tokens
        summary_lines.append(
            f"- **{src}**: {count} call(s), "
            f"{prompt_tokens} prompt tokens, {completion_tokens} completion tokens "
            f"(total {total_tokens})"
        )
    token_summary = calculate_token_usage_summary(model="gpt-3.5-turbo")
    summary_lines.append("\n---\n")
    summary_lines.append("\n## 💸 Token Usage Summary")
    summary_lines.append(f"- Prompt Tokens: {token_summary['prompt_tokens']}")
    summary_lines.append(f"- Completion Tokens: {token_summary['completion_tokens']}")
    summary_lines.append(f"- Total Tokens: {token_summary['total_tokens']}")
    summary_lines.append(f"- Estimated Cost ({token_summary['model']}): **${token_summary['estimated_cost_usd']:.4f} USD**")
    summary_lines.append("\n---\n")
    summary_lines.append("\n## 💸 Prompt + Response Preview")
    summary_lines.append(generate_openai_call_previews_md(n=20))

    # --- Write Summary File ---
    summary_path = output_dir / f"logging_summary_report_{run_id}.md"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    log_phase(f"✅ Logging Summary saved to: {summary_path}")

    # --- Convert to HTML and PDF ---
    html_path, pdf_path = convert_markdown_to_html_and_pdf_rfp(summary_path)

    return {
        "markdown": summary_path,
        "html": html_path,
        "pdf": pdf_path
    }


# Plot helper
def _plot_bar(data_dict, output_file, title):
    if not data_dict: return
    labels = list(data_dict.keys())
    values = list(data_dict.values())
    plt.figure(figsize=(8, 4))
    plt.barh(labels, values)
    plt.xlabel("Count")
    plt.title(title)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def display_openai_call_summary(n=10):
    from IPython.display import display, Markdown
    from pandas import DataFrame

    # Show call counts and token usage
    df = DataFrame(openai_call_log)
    if df.empty:
        print("No OpenAI calls logged.")
        return

    summary = df.groupby("source")[["prompt_tokens", "completion_tokens"]].sum()
    summary["total_tokens"] = summary.sum(axis=1)
    summary["% of total"] = 100 * summary["total_tokens"] / summary["total_tokens"].sum()
    display(Markdown("### 🔄 OpenAI Call Summary"))
    display(summary.sort_values("total_tokens", ascending=False))

    # Show a sample of calls
    display(Markdown(f"### 📋 Sample Calls (first {n})"))
    for i, row in df.head(n).iterrows():
        display(Markdown(f"""\
#### 🔹 Call #{i+1}
- **Source:** {row['source']}
- **Prompt tokens:** {row['prompt_tokens']}, Completion tokens: {row['completion_tokens']}

**Prompt Preview**:
{row['prompt'][:500]}
**Response Preview**:
{row['response'][:500]}
"""))
    
def generate_openai_call_previews_md(n=20):
    lines = []
    lines.append(f"## 📋 Sample OpenAI Calls (first {n})")

    if not openai_call_log:
        lines.append("_No OpenAI calls logged._")
        return "\n".join(lines)

    for i, call in enumerate(openai_call_log[:n]):
        lines.append(f"### 🔹 Call #{i + 1}")
        lines.append(f"- **Source:** {call['source']}")
        lines.append(f"- **Prompt tokens:** {call['prompt_tokens']}")
        lines.append(f"- **Completion tokens:** {call['completion_tokens']}")

        # Prompt preview
        prompt_data = call["prompt"]
        if isinstance(prompt_data, list):
            prompt_preview = " ".join(m.get("content", "") for m in prompt_data if isinstance(m, dict))
        else:
            prompt_preview = str(prompt_data)
        prompt_preview = prompt_preview.strip().replace("\n", " ")[:500]

        # Response preview
        response = call.get("response")
        call_type = call.get("call_type", "")
        if call_type == "chat.completion":
            try:
                response_text = response["choices"][0]["message"]["content"]
            except (KeyError, IndexError, TypeError):
                response_text = "[Malformed chat response]"
        elif call_type == "embedding":
            response_text = f"[Embedding vector of length {len(response['data'][0]['embedding'])}]"
        else:
            response_text = "[No valid response or unknown type]"
        response_preview = str(response_text).strip().replace("\n", " ")[:500]

        lines.append("**Prompt Preview:**")
        lines.append(f"```\n{prompt_preview}...\n```")

        lines.append("**Response Preview:**")
        lines.append(f"```\n{response_preview}...\n```")

        lines.append("")  # spacing

    return "\n".join(lines)


from src.utils.thought_analysis import cluster_thoughts_by_similarity

def generate_thought_summary_md(results):
    all_thoughts = []
    used_in_tool = 0

    for r in results:
        for tr in r.get("thought_records", []):
            all_thoughts.append(tr["text"])
            if tr.get("used_in_tool"):
                used_in_tool += 1

    total = len(all_thoughts)
    clusters = cluster_thoughts_by_similarity(all_thoughts, threshold=0.85)

    lines = []
    lines.append("## 🧠 Thought Quality & Redundancy")
    lines.append(f"- Total thoughts generated: {total}")
    lines.append(f"- Unique semantic clusters: {len(clusters)}")
    lines.append(f"- Thoughts reused in tools: {used_in_tool}/{total} ({used_in_tool / total:.0%})")

    # Optionally preview clusters
    if clusters and total < 50:
        lines.append("\n**Cluster Samples:**")
        for i, cluster in enumerate(clusters[:5]):
            lines.append(f"\n🔹 Cluster {i+1}:")
            for idx in cluster[:3]:
                lines.append(f"  - {all_thoughts[idx]}")
    return "\n".join(lines)

from src.utils.logging_utils import get_log_issues

def generate_log_health_md(log_path, max_lines=10):

    log_lines = get_log_issues(log_path, max_lines=max_lines)

    md_lines = ["## ⚠️ Log Health"]
    if not log_lines:
        md_lines.append("- ✅ No errors or warnings found in the log.\n")
    else:
        md_lines.append(f"- ❗ Found {len(log_lines)} issues in log (showing up to {max_lines}):")
        md_lines.extend([f"  - `{l}`" for l in log_lines[:max_lines]])

    return "\n".join(md_lines)


def generate_reasoning_trace_md(results, plots_dir="plots"):
    lines = ["## 🔍 Criterion Reasoning Trace\n"]

    # ==== Reasoning Trace by Criterion ====
    for res in results:
        trace = res.get("reasoning_trace", {})
        if not trace:
            continue
        lines.append("\n---\n")
        lines.append(f"### 🧠 Criterion: {trace['criterion']}")
        lines.append(f"**Final Score:** {trace['score']}")
        lines.append(f"**Explanation:** {trace['score_explanation']}\n")

        # ToT Thoughts
        lines.append("#### 🧠 Tree of Thought")
        for t in trace.get("tot_thoughts", []):
            used = "✅" if t["used_in_score"] else "❌"
            lines.append(f"- {used} Score {t['score']}: *{t['text']}*")

        # ReAct steps
        lines.append("\n#### 🤖 ReAct Steps")
        for step in trace.get("react_steps", []):
            used = "✅ Used in score" if step["used_in_score"] else "❌ Not used"
            success = "✅ Success" if step["tool_succeeded"] else "❌ Failed"
            lines.append(f"{step['step']}. 💭 *{step['thought']}*")
            lines.append(f"   ⚙️ `{step['action']}`")
            lines.append(f"   👁️ *Observation:* {step['observation']}")
            lines.append(f"   {used} | {success}")

        # Missing tools by section
        missing_tools = trace.get("missing_tools_by_section", {})
        if missing_tools:
            lines.append("\n#### 🧰 Missing Tools by Section")
            for section, tools in missing_tools.items():
                lines.append(f"\n##### 🔹 {section}")
                for tool_name, score in tools:
                    lines.append(f"- {tool_name}: Score {score:.3f}" if score is not None else f"- {tool_name}: No score available")

        # Auto-run tools
        auto_tools = trace.get("auto_tools_meta", [])
        if auto_tools:
            lines.append("\n#### 🤖 Auto-Run Tools")
            for tool in auto_tools:
                summary = tool["result"][:200].replace("\n", " ") + "..." if tool["result"] else "No result"
                sim_score = f"{tool['similarity_score']:.3f}" if tool.get("similarity_score") is not None else "N/A"
                lines.append(f"- `{tool['tool']}` for *{tool['criterion']}* (Score: {sim_score})")
                lines.append(f"  > {summary}")
    
        # === Reasoning Lineage Visualization ===
        try:
            from src.utils.reasoning_lineage import build_reasoning_graph, draw_reasoning_graph
            import matplotlib.pyplot as plt

            G = build_reasoning_graph(trace)
            filename = f"lineage_{trace['criterion'].replace(' ', '_')}.png"
            path = os.path.join(plots_dir, filename)

            # Save graph as PNG
            plt.clf()
            draw_reasoning_graph(G)
            plt.savefig(path)
            lines.append("\n### 🧠 Reasoning Lineage Graph")
            lines.append(f"![Lineage Graph]({path})")
        except Exception as e:
            lines.append(f"\n⚠️ Could not render reasoning graph: {e}")

    return "\n".join(lines)


def get_thought_deduplication_summary_md():
    stats = thought_dedup_stats
    lines = ["## 💠 Thought Deduplication Summary"]
    lines.append(f"- Total Thoughts Generated: {stats['total_generated']}")
    lines.append(f"- Unique Thoughts Retained: {stats['unique_retained']}")
    lines.append(f"- Redundant Thoughts Filtered: {stats['redundant_filtered']}")

    if stats["filtered_examples"]:
        lines.append("\n### 🔁 Sample Redundant Thoughts Filtered")
        for ex in stats["filtered_examples"]:
            lines.append(f"- {ex}")

    return "\n".join(lines)


def generate_embedding_cache_md():
    stats = get_embedding_cache_stats()
    total = stats["hits"] + stats["misses"]
    hit_rate = (stats["hits"] / total) * 100 if total > 0 else 0
    return f"""
## 🧠 Embedding Cache Usage
- Hits: {stats['hits']}
- Misses: {stats['misses']}
- Total Requests: {total}
- Cache Hit Rate: **{hit_rate:.1f}%**
""".strip()


def generate_reasoning_lineage_table_md(results):
    lines = ["## 🧠 Reasoning Lineage Table\n"]

    for res in results:
        trace = res.get("reasoning_trace", {})
        if not trace:
            continue

        lines.append(f"\n### 🔹 {trace['criterion']}\n")
        lines.append("| Step | Thought | Source | Action | Observation | Used in Score | Tool Success |")
        lines.append("|------|---------|--------|--------|-------------|----------------|---------------|")

        # ToT thoughts
        for i, t in enumerate(trace.get("tot_thoughts", [])):
            lines.append(f"| ToT-{i+1} | {t['text']} | ToT | — | — | {'✅' if t['used_in_score'] else '❌'} | — |")

        # ReAct steps
        for step in trace.get("react_steps", []):
            lines.append(
                f"| Step {step['step']} | {step['thought']} | ReAct | `{step['action']}` | {step['observation'][:40]}... "
                f"| {'✅' if step['used_in_score'] else '❌'} | {'✅' if step['tool_succeeded'] else '❌'} |"
            )

    return "\n".join(lines)

