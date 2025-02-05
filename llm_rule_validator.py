import json
import logging
import uuid
from typing import Dict, List

from litellm import completion

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Define log format with timestamp
                    datefmt='%Y-%m-%d %H:%M:%S'  # Customize the timestamp format
                    )

logger = logging.getLogger(__name__)

def format_rules_for_prompt(existing_rules: List[Dict]) -> str:
    """Format existing rules for the prompt"""
    formatted_rules = "Existing rules:\n"
    for i, rule in enumerate(existing_rules, 1):
        formatted_rules += f"{json.dumps(existing_rules)}"
    return formatted_rules


class LLMSemanticValidator:
    def __init__(self, model_name: str = "gemini/gemini-1.5-flash"):
        """Initialize the SemanticValidator with LLM integration"""
        self.model = model_name
        self.system_prompt = """You are a rule validation assistant. Your task is to:
        1. Check for any direct contradictions between rules  ignore non existent cases
        2. Ignore potential or non direct contradictions
        3. Identify any ambiguous statements
        4. Detect any direct redundant rules
        5. Ignore potential or non direct redundancies between rules
        6. Narrower scope overcomes redundancy  
        7. Use only given states of rules donot make assumptions
        8. Do not guess for additions or modifications of rules
        9. Similar entities should be grouped together
        10. Respond with a structured analysis
        """

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better analysis"""
        if not isinstance(text, str):
            return ""
        return ' '.join(text.strip().split())

    def analyze_rule(self, new_rule: Dict, existing_rules: List[Dict]) -> Dict:
        """Analyze new rule against existing rules using LLM"""

        # Format the prompt
        existing_rules_text = format_rules_for_prompt(existing_rules)
        new_rule_text = f"New rule to validate:\n{json.dumps(new_rule)}"

        prompt = f"""
{existing_rules_text}

{new_rule_text}

Please carefully analyze the new rule.

Format your response exactly as follows:

Can coexist with other rules: [true/false]
Direct Contradictions: [list of contradictions]
Ambiguous Statements: [list of ambiguous statements]
Redundant Rules: [list of redundant rules]
Grouping of Similar Entities: [grouping details]
Structured Analysis Summary: [summary]
"""
        logger.info(self.system_prompt + "\n" + prompt)
        try:
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=1
            )

            # Parse LLM response
            analysis = response.choices[0].message.content
            logger.info(analysis)

            # Extract information from the response
            lines = analysis.split('\n')
            can_coexist = None
            direct_contradictions = []
            ambiguous_statements = []
            redundant_rules = []
            grouping_of_similar_entities = ""
            structured_analysis_summary = ""

            for line in lines:
                if line.startswith("Can coexist with other rules:"):
                    can_coexist = "true" in line.split(":")[1].strip().lower()
                elif line.startswith("Direct Contradictions:"):
                    direct_contradictions = line.split(":")[1].strip().split(", ")
                elif line.startswith("Ambiguous Statements:"):
                    ambiguous_statements = line.split(":")[1].strip().split(", ")
                elif line.startswith("Redundant Rules:"):
                    redundant_rules = line.split(":")[1].strip().split(", ")
                elif line.startswith("Grouping of Similar Entities:"):
                    grouping_of_similar_entities = line.split(":")[1].strip()
                elif line.startswith("Structured Analysis Summary:"):
                    structured_analysis_summary = line.split(":")[1].strip()

            # Determine if there are issues
            has_issues = not can_coexist or '[]' not in direct_contradictions  or '[]' not in ambiguous_statements or '[]' not in redundant_rules

            return {
                "has_issues": has_issues,
                "can_coexist": can_coexist,
                "direct_contradictions": direct_contradictions,
                "ambiguous_statements": ambiguous_statements,
                "redundant_rules": redundant_rules,
                "grouping_of_similar_entities": grouping_of_similar_entities,
                "structured_analysis_summary": structured_analysis_summary
            }

        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            return {
                "has_issues": True,
                "can_coexist": False,
                "direct_contradictions": [],
                "ambiguous_statements": [],
                "redundant_rules": [],
                "grouping_of_similar_entities": "",
                "structured_analysis_summary": f"Error in analysis:\n{str(e)}"
            }


def validate_rule(new_rule: Dict, existing_rules: List[Dict]) -> Dict:
    """Validate a new rule using LLM analysis"""
    validator = LLMSemanticValidator()

    # Analyze the rule
    analysis_result = validator.analyze_rule(new_rule, existing_rules)

    if analysis_result["has_issues"]:
        return {
            "is_valid": False,
            "message": "Issues detected in rule validation",
            "details": analysis_result
        }

    # If valid, generate and return rule ID
    rule_id = str(uuid.uuid4())
    return {
        "is_valid": True,
        "message": "Rule is valid",
        "details": analysis_result,
        "rule_id": rule_id
    }
