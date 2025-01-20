import json

import streamlit as st

from rule_manager import RuleManager
from semantic_validator import validate_rule
from title_generator import generate_title


def load_rules():
    try:
        with open('rules_repository.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_rules(rules):
    with open('rules_repository.json', 'w') as f:
        json.dump(rules, f, indent=2)


def main():
    st.title("Rule Management System")

    # Initialize session state
    if 'rules' not in st.session_state:
        st.session_state.rules = load_rules()

    rule_manager = RuleManager()

    # Input form
    with st.form("rule_input_form"):
        context = st.text_area("Rule Context", height=400)

        submitted = st.form_submit_button("Submit Rule")

        if submitted and context:
            # Generate title using Gemini
            title = generate_title(context)

            # Create rule object
            new_rule = {
                "title": title,
                "context": context
            }

            # Validate rule against existing rules
            validation_result = validate_rule(new_rule, st.session_state.rules)

            if validation_result["is_valid"]:
                st.session_state.rules.append(new_rule)
                save_rules(st.session_state.rules)
                st.success(f"Rule saved successfully! Generated title: {title}")
            else:
                st.error(f"Rule validation failed: {validation_result['message']}")

    # Display existing rules
    if st.session_state.rules:
        st.subheader("Existing Rules")
        for idx, rule in enumerate(st.session_state.rules):
            with st.expander(f"Rule {idx + 1}: {rule['title']}"):
                st.write("Context:", rule["context"])
                st.write("Title:", rule["title"])



if __name__ == "__main__":
    main()
