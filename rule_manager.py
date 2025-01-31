import json
import logging
from datetime import datetime

from vector_db import VectorDB


class RuleManager:
    def __init__(self, repository_file='rules_repository.json'):
        self.repository_file = repository_file
        self.rules = self.load_rules()
        self.vector_db = VectorDB()

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

    def add_rule(self, rule, rule_id=None):
        """Add a new rule to the repository"""
        rule['created_at'] = datetime.now().isoformat()
        if rule_id:
            rule['rule_id'] = rule_id
        self.rules.append(rule)
        self.save_rules()

    def delete_rule(self, index):
        """Delete a rule and its embeddings"""
        if 0 <= index < len(self.rules):
            rule = self.rules[index]
            rule_id = rule.get('rule_id')
            logging.info("ENTER DELETE")
            # Delete from vector database if rule_id exists
            try:
                if rule_id:
                    self.vector_db.delete_rule_embeddings(rule_id)
            except Exception as e:
                logging.error(f"no deletion for {rule_id} {e}")
            logging.info("HAPPY")
            del self.rules[index]
            self.save_rules()
            return True
        return False

    def update_rule(self, index, updated_rule):
        """Update an existing rule and its embeddings"""
        if 0 <= index < len(self.rules):
            old_rule = self.rules[index]
            old_rule_id = old_rule.get('rule_id')
            
            # Delete old embeddings
            if old_rule_id:
                self.vector_db.delete_rule_embeddings(old_rule_id)
            
            # Update rule
            self.rules[index].update(updated_rule)
            self.save_rules()
            return True
        return False
    def update_rule(self, index: int, updated_rule: dict) -> bool:
        """Update an existing rule"""
        try:
            old_rule_id = self.rules[index].get('rule_id')

            # Delete old embeddings
            if old_rule_id:
                self.vector_db.delete_rule_embeddings(old_rule_id)
            rules = self.get_rules()
            if 0 <= index < len(rules):
                rules[index] = updated_rule
                self.save_rules()

                return True
            return False
        except Exception as e:
            logging.error(f"Error updating rule: {str(e)}")
            return False

    def get_rules(self):
        """Get all rules from the repository"""
        return self.rules