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

# Tool usage tracker
tool_stats = defaultdict(int)
thought_stats = defaultdict(int)
thought_score_stats = defaultdict(int)
openai_call_counter = 0

def log_phase(message):
    logger.info(f"📌 {message}")

def log_result(vendor, criterion, score):
    logger.info(f"✅ [{vendor}] '{criterion}' scored {score}/10")

def log_tool_used(tool_name):
    tool_stats[tool_name] += 1
    logger.debug(f"⚙️ Tool used: {tool_name}")

def log_thought_score(thought, score):
    thought_stats[thought] += 1
    thought_score_stats[score] += 1
    logger.debug(f"💭 Thought scored: {thought} with score {score}")

def log_openai_call(prompt, response):
    global openai_call_counter
    openai_call_counter += 1
    logger.debug(f"🔄 OpenAI call #{openai_call_counter}: {prompt} -> {response}")

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

def print_openai_call_stats():
    logger.info(f"🔄 Total OpenAI calls made: {openai_call_counter}")

def log_tool_execution(tool_name, tool_fn, input_arg=None, agent=None):
    fn_module = inspect.getmodule(tool_fn).__name__
    input_preview = input_arg[:100] + "..." if input_arg and len(input_arg) > 100 else input_arg
    log_phase(f"🧪 Executing tool: {tool_name} from {fn_module}")
    if input_arg:
        log_phase(f"🔹 Input: {input_preview}")
    if agent and hasattr(agent, 'section_name'):
        log_phase(f"📄 Section: {agent.section_name}")

def setup_logging(log_file="logs/eval.log"):
    logger = logging.getLogger("ProposalEvaluator")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")

    # Console output
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # File output
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_path)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

def display_log(log_file="logs/eval_notebook_run.log"):
    from IPython.display import display, Markdown
    with open(log_file) as f:
        log_text = f.read()
    display(Markdown(f"```\n{log_text}\n```"))
