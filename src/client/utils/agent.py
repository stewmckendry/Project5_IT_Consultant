# utils/agent.py

class ReActConsultantAgent:
    def __init__(self, section_name, section_text, model="gpt-3.5-turbo", temperature=0.6):
        self.section_name = section_name
        self.section_text = section_text
        self.model = model
        self.temperature = temperature
        self.history = []  # [(thought, action, observation)]
        self.memory = {
            "tool_history": [],
            "section_notes": {},
            "section_scores": {},
            "section_fixes": {},
            "confidence_levels": {},
            "cross_section_flags": [],
            "citations": [],
            "missing_analysis": "",
            "debug_notes": {}
        }
        self.tool_usage = {}

    def build_react_prompt_withTools(self):
        from utils.tools import build_tool_hints, format_tool_catalog_for_prompt, tool_catalog

        tool_hint_text, tools_to_focus = build_tool_hints(self)
        base_prompt = (
            f"You are an expert IT strategy consultant reviewing a report section titled '{self.section_name}'.\n"
            "You are using ReAct (Reason + Act) to think through the review.\n\n"
            "Format each response like this:\n"
            "Thought: <your reasoning>\n"
            f"Action: <one of: {tool_hint_text}>\n\n"
        )
        base_prompt += format_tool_catalog_for_prompt(tool_catalog)
        base_prompt += f"Here is the section content:\n{self.section_text}\n\n"

        for step in self.history:
            base_prompt += f"Thought: {step['thought']}\n"
            base_prompt += f"Action: {step['action']}\n"
            base_prompt += f"Observation: {step['observation']}\n\n"

        base_prompt += "What is your next Thought and Action?"
        return [{"role": "user", "content": base_prompt}]
