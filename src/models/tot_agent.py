# src/models/tot_agent.py

from src.models.openai_interface import call_openai_with_tracking
import uuid
from src.utils.logging_utils import log_phase, log_thought_score, log_result, print_tool_stats

# --- Tree Node Class ---
class TreeNode:
    """
    Represents a node in the Tree of Thought (ToT) reasoning process.

    Purpose:
    This class models a single node in the reasoning tree, which includes a thought, its score, a reference to its parent node, and its children nodes. It provides methods to traverse the tree and retrieve the reasoning path.

    Parameters:
    - thought (str): The thought or reasoning step represented by this node.
    - score (float): The score or evaluation of this thought. Default is 0.
    - parent (TreeNode): The parent node of this node. Default is None.

    Functions:
    - __init__: Initializes the node with a thought, score, parent, and generates a unique ID.
    - path: Retrieves the reasoning path from the root to this node.

    Workflow:
    1. Initializes a unique ID for the node using UUID.
    2. Stores the thought, score, and parent node.
    3. Maintains a list of child nodes.
    4. Provides a `path` method to retrieve the reasoning path from the root to this node.

    Returns:
    - TreeNode: An instance of the TreeNode class representing a reasoning step in the ToT process.
    """

    def __init__(self, thought, score=0, parent=None):
        self.id = str(uuid.uuid4())
        self.thought = thought
        self.score = score
        self.parent = parent
        self.children = []

    def path(self):
        node, result = self, []
        while node:
            result.append(node.thought)
            node = node.parent
        return list(reversed(result))


# --- Basic ToT Agent ---


class SimpleToTAgent:
    """
    Represents a simple Tree of Thought (ToT) reasoning agent.

    Purpose:
    This class models a basic agent that uses a Tree of Thought approach to evaluate a given section of a proposal against a specific criterion. It generates thoughts, evaluates them, and selects the best reasoning path.

    Parameters:
    - llm (callable): A language model function that generates thoughts based on a prompt.
    - scorer (callable): A scoring function that evaluates the quality of a thought.
    - beam_width (int): The number of top thoughts to keep at each depth. Default is 2.
    - max_depth (int): The maximum depth of the reasoning tree. Default is 2.

    Functions:
    - __init__: Initializes the agent with the provided LLM, scorer, beam width, and maximum depth.
    - generate_thoughts: Generates thoughts for a given section and criterion using the LLM.
    - evaluate_and_select: Evaluates and selects the top thoughts based on their scores.
    - run: Constructs a reasoning tree by iteratively expanding thoughts up to the maximum depth and returns the best reasoning path and its score.

    Workflow:
    1. Initializes the agent with the provided LLM, scorer, beam width, and maximum depth.
    2. Generates thoughts for a given section and criterion using the LLM.
    3. Evaluates and selects the top thoughts based on their scores.
    4. Constructs a reasoning tree by iteratively expanding thoughts up to the maximum depth.
    5. Returns the best reasoning path and its score.

    Returns:
    - SimpleToTAgent: An instance of the SimpleToTAgent class capable of performing Tree of Thought reasoning.
    """

    def __init__(self, llm, scorer, beam_width=2, max_depth=2):
        self.llm = llm
        self.scorer = scorer
        self.beam_width = beam_width
        self.max_depth = max_depth

    def generate_thoughts(self, section, criterion, parent_node):
        base_prompt = f"""
    You are evaluating a technology vendor proposal for the criterion: **{criterion}**.

    Proposal excerpt:
    \"\"\"
    {section}
    \"\"\"

    Current reasoning path: {" -> ".join(parent_node.path()[1:]) if parent_node.thought != "ROOT" else "(start)"}

    What are the next 3 useful thoughts or questions that could help you assess the proposal based on this criterion?
    Respond with a numbered list.
    """
        response = self.llm(base_prompt)

        # Parse the LLM output into individual thoughts
        thoughts = [
            t.strip("123. ").strip("-• ") for t in response.split("\n") if t.strip()
        ]  # strips #s, -, and parses thoughs by line break
        return thoughts[:3]

    def evaluate_and_select(self, nodes):
        for node in nodes:
            node.score = self.scorer(node.thought)
        return sorted(nodes, key=lambda n: n.score, reverse=True)[: self.beam_width]

    def run(self, section, criterion):
        root = TreeNode("ROOT")
        frontier = [root]

        for depth in range(self.max_depth):
            log_phase(
                f"\n🔁 Expanding depth {depth + 1}/{self.max_depth} — Frontier size: {len(frontier)}"
            )
            next_frontier = []

            for node in frontier:
                thoughts = self.generate_thoughts(section, criterion, node)
                log_phase(f"💡 Thoughts generated from: '{node.thought}'")
                log_phase("\n".join(f"  → {t}" for t in thoughts))

                if not thoughts:
                    log_phase("⚠️ No thoughts returned. Skipping.")
                    continue

                child_nodes = [TreeNode(thought=t, parent=node) for t in thoughts]
                top_children = self.evaluate_and_select(child_nodes)

                for child in top_children:
                    log_phase(f"✅ Selected: {child.thought} (score: {child.score})")

                node.children.extend(top_children)
                next_frontier.extend(top_children)

            frontier = next_frontier

            if not frontier:
                log_phase("⚠️ No more frontier nodes. Stopping early.")
                break

        if frontier:
            best_leaf = max(
                frontier, key=lambda n: n.score
            )  # Get the best leaf node based on score
            return {
                "criterion": criterion,
                "score": best_leaf.score,
                "reasoning_path": best_leaf.path()[1:],  # skip 'ROOT'
            }
        else:
            return {
                "criterion": criterion,
                "score": 0,
                "reasoning_path": ["No valid thoughts generated."],
            }


def generate_thoughts_openai(prompt, model="gpt-3.5-turbo", temperature=0.3):
    messages = [
        {"role": "system", "content": "You are an expert evaluator of RFP proposals."},
        {"role": "user", "content": prompt}
    ]
    return call_openai_with_tracking(messages, model=model, temperature=temperature)


def score_thought_with_openai(thought, criterion, section, model="gpt-3.5-turbo"):
    """
    Purpose:
    Scores a thought generated by an AI agent for assessing a technology proposal based on its relevance, clarity, and usefulness.

    Parameters:
    - thought (str): The thought or reasoning step to be evaluated.
    - criterion (str): The evaluation criterion against which the thought is being assessed.
    - section (str): The proposal section being evaluated.
    - model (str): The name of the OpenAI model to use for scoring. Default is "gpt-3.5-turbo".

    Workflow:
    1. Constructs a prompt that includes the proposal section, evaluation criterion, and the thought to be scored.
    2. Sends the prompt to the OpenAI API using the `call_openai_with_tracking` function.
    3. Prints the thought being scored and the response from the LLM.
    4. Attempts to parse the response as an integer score between 1 and 10.
    5. If parsing fails, defaults to a fallback score of 5.

    Returns:
    - int: The score assigned to the thought, ranging from 1 to 10.
    """
    prompt = f"""
    You are evaluating a thought generated by an AI agent for assessing a technology proposal.

    Use this rubric to assign a score from 1 to 10:

    - 9–10: Insightful, highly relevant, and clearly advances evaluation.
    - 7–8: Solid, useful thought, but not exceptionally insightful.
    - 4–6: Somewhat helpful, but vague or redundant.
    - 1–3: Not useful, unclear, or irrelevant.

    Proposal:
    \"\"\"
    {section}
    \"\"\"

    Criterion: {criterion}
    Thought: "{thought}"

    Respond with a single number only, from 1 to 10.
    """
    messages = [{"role": "user", "content": prompt}]
    response = call_openai_with_tracking(messages, model=model, temperature=0)

    log_phase("\n🧠 Scoring Thought:")
    log_phase(f"→ {thought}")
    log_phase(f"📩 LLM Response: {response}")

    try:
        score = int(response.strip())
        log_phase(f"✅ Parsed Score: {score}/10")
        log_thought_score(thought, score)
        return score
    except ValueError:
        log_phase("⚠️ Failed to parse score, using fallback score = 5")
        log_thought_score(thought, 5)
        return 5