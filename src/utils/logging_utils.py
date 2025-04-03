import logging
from collections import defaultdict
import inspect
from pathlib import Path
import os

# Initialize logger
logger = logging.getLogger("ProposalEvaluator")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

# Initialize global variables / custom trackers
tool_stats = defaultdict(int)
tool_failure_stats = defaultdict(int)    # failed calls
tool_failure = {}
tool_skipped_stats = defaultdict(int)    # failed calls
tool_skipped = {}
thought_stats = defaultdict(int)
thought_score_stats = defaultdict(int)
openai_call_log = []
openai_call_counter = 0
openai_call_times = []
openai_call_sources = defaultdict(int)
openai_prompt_token_usage_by_source = defaultdict(int)
openai_completion_token_usage_by_source = defaultdict(int)
#tool_call_times = defaultdict(list)
thought_dedup_stats = {
    "total_generated": 0,
    "unique_retained": 0,
    "redundant_filtered": 0,
    "filtered_examples": []
}


def log_phase(message):
    logger.info(f"📌 {message}")

def log_result(vendor, criterion, score):
    logger.info(f"✅ [{vendor}] '{criterion}' scored {score}/10")

def log_tool_used(tool_name):
    tool_stats[tool_name] += 1
    logger.debug(f"⚙️ Tool used: {tool_name}, total calls: {tool_stats[tool_name]}")

def log_thought_score(thought, score):
    thought_stats[thought] += 1
    thought_score_stats[score] += 1
    logger.debug(f"💭 Thought scored: {thought} with score {score}")

def log_openai_call(prompt, response, source=None, prompt_tokens=0, completion_tokens=0, embedding=True):
    global openai_call_counter
    openai_call_counter += 1

    openai_call_sources[source] += 1
    openai_prompt_token_usage_by_source[source] += prompt_tokens
    openai_completion_token_usage_by_source[source] += completion_tokens

    if embedding:
        openai_call_log.append({
            "source": source,
            "call_type": "embedding",
            "prompt": prompt,
            "response": response.model_dump(),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens
        })
        log_msg = (
            f"🔄 OpenAI call #{openai_call_counter} from {source}: "
            f"Embedding call, no response logged and no token usage stats. "
        )
    else:
        openai_call_log.append({
            "source": source,
            "call_type": "chat.completion",
            "prompt": prompt,
            "response": response.model_dump(),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens
        })
        log_msg = (
            f"🔄 OpenAI call #{openai_call_counter} from {source}: "
            f"{prompt[:50]}... -> {str(response)[:50]}... "
            f"(Prompt tokens: {prompt_tokens}, Completion tokens: {completion_tokens})"
        )
    logger.info(log_msg)


def print_tool_stats():
    logger.info("📊 Tool usage summary:")
    for tool, count in tool_stats.items():
        logger.info(f"   {tool}: {count} time(s)")

def print_thought_stats():
    logger.info("📊 Thought generation summary:")
    score_distribution = defaultdict(int)
    for score, count in thought_score_stats.items():
        score_distribution[score] += count
    for score, count in sorted(score_distribution.items(), reverse=True):
        logger.info(f"   Thought score {score}: {count} time(s)")

def log_tool_execution(tool_name, tool_fn, input_arg=None, agent=None):
    fn_module = inspect.getmodule(tool_fn).__name__
    input_preview = input_arg[:100] + "..." if input_arg and len(input_arg) > 100 else input_arg
    log_phase(f"🧪 Executing tool: {tool_name} from {fn_module}")
    if input_arg:
        log_phase(f"🔹 Input: {input_preview}")
    if agent and hasattr(agent, 'section_name'):
        log_phase(f"📄 Section: {agent.section_name}")

def log_tool_failed(tool_name, error_message):
    tool_failure[tool_name] = error_message
    tool_failure_stats[tool_name] += 1
    logger.error(f"❌ Tool '{tool_name}' failed: {error_message}")

def log_tool_skipped(tool_name, error_message):
    tool_skipped[tool_name] = error_message
    tool_skipped_stats[tool_name] += 1
    logger.error(f"❌ Tool '{tool_name}' skipped: {error_message}")

def log_openai_call_time(duration_sec):
    openai_call_times.append(duration_sec)

def get_openai_call_avg_time():
    total = len(openai_call_times)
    avg = sum(openai_call_times) / total if total > 0 else 0
    return avg

def print_openai_call_stats():
    total = len(openai_call_times)
    avg = get_openai_call_avg_time()
    logger.info(f"🔄 Total OpenAI calls: {total}, Avg time: {round(avg, 2)} sec")

def setup_logging(log_file="logs/eval.log"):
    global current_log_file
    current_log_file = log_file

    logger = logging.getLogger("ProposalEvaluator")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")

    # Always ensure console logging
    has_console = any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    if not has_console:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    # Add file logging if not already present
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    has_file = any(isinstance(h, logging.FileHandler) and h.baseFilename == str(log_path.resolve()) for h in logger.handlers)
    if not has_file:
        fh = logging.FileHandler(log_path)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    log_phase("Logging initialized")
    log_phase(f"Log file: {log_file}")
    return logger


def display_log(log_file="logs/eval_notebook_run.log"):
    from IPython.display import display, Markdown
    with open(log_file) as f:
        log_text = f.read()
    display(Markdown(f"```\n{log_text}\n```"))


def print_tool_success_rates():
    logger.info("📊 Tool Success Rates:")
    for tool, total_calls in tool_stats.items():
        failures = tool_failure_stats.get(tool, 0)
        success = total_calls - failures
        rate = (success / total_calls) * 100 if total_calls > 0 else 0
        logger.info(f"   {tool}: {success}/{total_calls} successful ({rate:.1f}%)")


def print_openai_call_sources():
    logger.info("📍 OpenAI Calls by Source:")
    for src, count in openai_call_sources.items():
        logger.info(f"   {src}: {count} call(s)")


def calculate_token_usage_summary(model="gpt-3.5-turbo"):
    total_prompt_tokens = sum(openai_prompt_token_usage_by_source.values())
    total_completion_tokens = sum(openai_completion_token_usage_by_source.values())
    total_tokens = total_prompt_tokens + total_completion_tokens

    # Pricing (update if you switch models)
    pricing = {
        "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
    }

    if model not in pricing:
        raise ValueError(f"Unknown model '{model}'. Add to pricing dict.")

    prompt_rate = pricing[model]["prompt"]
    completion_rate = pricing[model]["completion"]

    total_cost = (
        (total_prompt_tokens / 1000) * prompt_rate +
        (total_completion_tokens / 1000) * completion_rate
    )

    return {
        "model": model,
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(total_cost, 4)
    }


def get_log_issues(log_file_path=None, levels=("ERROR", "WARNING", "CRITICAL"), max_lines=10):
    """
    Reads the log file and returns a list of relevant lines based on log levels.
    """
    log_path = Path(log_file_path or current_log_file or "logs/eval.log")

    if not log_path.exists():
        return []

    matched = []
    for line in log_path.read_text().splitlines():
        if any(f"[{level.upper()}]" in line.upper() for level in levels):
            matched.append(line.strip())
        if len(matched) >= max_lines:
            break

    return matched


def log_deduplication(thoughts, unique_thoughts):
    deduped = [t for t in thoughts if t not in unique_thoughts]
    thought_dedup_stats["total_generated"] += len(thoughts)
    thought_dedup_stats["unique_retained"] += len(unique_thoughts)
    thought_dedup_stats["redundant_filtered"] += len(deduped)
    thought_dedup_stats["filtered_examples"].extend(deduped[:3])  # limit to 3 for brevity

def reset_dedup_stats():
    thought_dedup_stats.update({
        "total_generated": 0,
        "unique_retained": 0,
        "redundant_filtered": 0,
        "filtered_examples": []
    })