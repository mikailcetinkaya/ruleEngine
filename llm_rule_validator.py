import logging
import uuid
from typing import Dict, List

from litellm import completion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticValidator:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """Initialize the SemanticValidator with LLM integration"""
        self.model = model_name
        self.system_prompt = """You are a rule validation assistant. Your task is to:
        1. Check for contradictions between rules
        2. Identify any ambiguous statements
        3. Detect overlapping content or redundant rules
        4. Respond with a structured analysis
        
        Respond with:
        - has_issues: true/false
        - issues_found: list of specific issues
        - explanation: detailed explanation of each issue"""

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better analysis"""
        if not isinstance(text, str):
            return ""
        return ' '.join(text.strip().split())

    def format_rules_for_prompt(self, existing_rules: List[Dict]) -> str:
        """Format existing rules for the prompt"""
        formatted_rules = "Existing rules:\n"
        for i, rule in enumerate(existing_rules, 1):
            formatted_rules += f"{i}. {rule.get('title', 'Untitled')}: {rule.get('context', '')}\n"
        return formatted_rules

    def analyze_rule(self, new_rule: Dict, existing_rules: List[Dict]) -> Dict:
        """Analyze new rule against existing rules using LLM"""

        # Format the prompt
        existing_rules_text = self.format_rules_for_prompt(existing_rules)
        new_rule_text = f"New rule to validate:\n{new_rule.get('title', 'Untitled')}: {new_rule.get('context', '')}"

        prompt = f"""
        {existing_rules_text}
        
        {new_rule_text}
        
        Analyze the new rule for:
        1. Contradictions with existing rules
        2. Ambiguous statements
        3. Overlapping content with existing rules
        
        Provide a structured response with:
        - Whether there are any issues (true/false)
        - List of specific issues found
        - Detailed explanation for each issue
        """

        try:
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            # Parse LLM response
            analysis = response.choices[0].message.content

            # Simple parsing (you might want to make this more robust)
            has_issues = "true" in analysis.lower()

            return {
                "has_issues": has_issues,
                "analysis": analysis
            }

        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            return {
                "has_issues": True,
                "analysis": f"Error in analysis: {str(e)}"
            }

def validate_rule(new_rule: Dict, existing_rules: List[Dict]) -> Dict:
    """Validate a new rule using LLM analysis"""
    validator = SemanticValidator()

    # Analyze the rule
    analysis_result = validator.analyze_rule(new_rule, existing_rules)

    if analysis_result["has_issues"]:
        return {
            "is_valid": False,
            "message": "Issues detected in rule validation",
            "details": analysis_result["analysis"]
        }

    # If valid, generate and return rule ID
    rule_id = str(uuid.uuid4())
    return {
        "is_valid": True,
        "message": "Rule is valid",
        "details": analysis_result["analysis"],
        "rule_id": rule_id
    }
