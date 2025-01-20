import json
from datetime import datetime


class RuleManager:
    def __init__(self, repository_file='rules_repository.json'):
        self.repository_file = repository_file
        self.rules = self.load_rules()

    def load_rules(self):
        """Load rules from the repository file"""
        try:
            with open(self.repository_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_rules(self):
        """Save rules to the repository file"""
        with open(self.repository_file, 'w') as f:
            json.dump(self.rules, f, indent=2)

    def add_rule(self, rule):
        """Add a new rule to the repository"""
        rule['created_at'] = datetime.now().isoformat()
        self.rules.append(rule)
        self.save_rules()

    def get_rules(self):
        """Get all rules from the repository"""
        return self.rules

    def delete_rule(self, index):
        """Delete a rule by index"""
        if 0 <= index < len(self.rules):
            del self.rules[index]
            self.save_rules()
            return True
        return False

    def update_rule(self, index, updated_rule):
        """Update an existing rule"""
        if 0 <= index < len(self.rules):
            self.rules[index].update(updated_rule)
            self.save_rules()
            return True
        return False
