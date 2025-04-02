from pathlib import Path
from datetime import datetime
from matplotlib import pyplot as plt
import shutil
import json
from src.utils.logging_utils import openai_call_log

def finalize_evaluation_run(output_dir="../outputs/proposal_eval_reports", logs_dir="logs", run_id=None):
    from src.utils import logging_utils  # adjust if needed
    run_id = run_id or datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logs_dir = Path(logs_dir)
    logs_dir.mkdir(exist_ok=True)
    img_dir = logs_dir / "plots"
    img_dir.mkdir(exist_ok=True)

    summary_lines = []
    summary_lines.append(f"# 📊 Evaluation Summary Report – `{run_id}`\n")

    # --- TOOL USAGE ---
    summary_lines.append("## 🔧 Tool Usage")
    for tool, count in logging_utils.tool_stats.items():
        summary_lines.append(f"- {tool}: {count} time(s)")
    _plot_bar(logging_utils.tool_stats, img_dir / "tool_usage.png", "Tool Usage")
    summary_lines.append("![Tool Usage](plots/tool_usage.png)\n")

    # --- THOUGHT SCORE DIST ---
    summary_lines.append("## 💭 Thought Score Distribution")
    for score, count in sorted(logging_utils.thought_score_stats.items(), reverse=True):
        summary_lines.append(f"- Score {score}: {count} thought(s)")
    _plot_bar(logging_utils.thought_score_stats, img_dir / "thought_scores.png", "Thought Scores")
    summary_lines.append("![Thought Scores](plots/thought_scores.png)\n")

    # --- FAILURES ---
    summary_lines.append("## ❗ Tool Failures")
    for tool, reason in logging_utils.tool_failure.items():
        summary_lines.append(f"- {tool}: {reason}")
    
    # --- TOOL SUCCESS RATES ---
    summary_lines.append("## ✅ Tool Success Rates")
    for tool, total in logging_utils.tool_stats.items():
        fail = logging_utils.tool_failure_stats.get(tool, 0)
        success = total - fail
        rate = (success / total) * 100 if total else 0
        summary_lines.append(f"- {tool}: {success}/{total} successful ({rate:.1f}%)")

    # --- OPENAI CALLS ---
    summary_lines.append("## 🔄 OpenAI API Calls")
    summary_lines.append(f"- Total Calls: {logging_utils.openai_call_counter}")
    avg_time = logging_utils.get_openai_call_avg_time()
    summary_lines.append(f"- Average Time: {avg_time:.2f} sec")
    summary_lines.append(f"- OpenAI Call Sources & Token Usage")
    for src, count in logging_utils.openai_call_sources.items():
        prompt_tokens = logging_utils.openai_prompt_token_usage_by_source.get(src, 0)
        completion_tokens = logging_utils.openai_completion_token_usage_by_source.get(src, 0)
        total_tokens = prompt_tokens + completion_tokens
        summary_lines.append(
            f"- **{src}**: {count} call(s), "
            f"{prompt_tokens} prompt tokens, {completion_tokens} completion tokens "
            f"(total {total_tokens})"
        )
    token_summary = logging_utils.calculate_token_usage_summary(model="gpt-3.5-turbo")
    summary_lines.append("\n## 💸 Token Usage Summary")
    summary_lines.append(f"- Prompt Tokens: {token_summary['prompt_tokens']}")
    summary_lines.append(f"- Completion Tokens: {token_summary['completion_tokens']}")
    summary_lines.append(f"- Total Tokens: {token_summary['total_tokens']}")
    summary_lines.append(f"- Estimated Cost ({token_summary['model']}): **${token_summary['estimated_cost_usd']:.4f} USD**")
    summary_lines.append("\n## 💸 Prompt + Response Preview")
    summary_lines.append(generate_openai_call_previews_md(n=20))

    # --- Write Summary File ---
    summary_path = logs_dir / f"eval_summary_{run_id}.md"
    summary_path.write_text("\n".join(summary_lines))
    print(f"✅ Summary saved to: {summary_path}")

    # --- Zip Logs + Outputs ---
    archive_name = f"eval_archive_{run_id}"
    archive_path = shutil.make_archive(archive_name, "zip", root_dir=".", base_dir=output_dir)
    final_zip = logs_dir / f"{archive_name}.zip"
    shutil.move(archive_path, final_zip)
    print(f"✅ Zipped outputs to: {final_zip}")

    return {
        "summary_path": summary_path,
        "plots_dir": img_dir,
        "zip_path": final_zip
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

        if call_type == "chat.completion" and response and hasattr(response, "choices"):
            response_text = response.choices[0].message.content
        elif call_type == "embedding" and response and hasattr(response, "data"):
            response_text = f"[Embedding vector of length {len(response.data[0].embedding)}]"
        else:
            response_text = "[No valid response or unknown type]"

        response_preview = str(response_text).strip().replace("\n", " ")[:500]

        lines.append("**Prompt Preview:**")
        lines.append(f"```text\n{prompt_preview}...\n```")

        lines.append("**Response Preview:**")
        lines.append(f"```text\n{response_preview}...\n```")

        lines.append("")  # spacing

    return "\n".join(lines)
