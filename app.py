import json
import logging
from typing import List, Dict

import streamlit as st

from rule_manager import RuleManager
from llm_rule_validator import validate_rule
from title_generator import generate_title


def format_rule_context(context: str) -> str:
    """Format rule context with proper line breaks and styling"""
    # Split by explicit line breaks and filter empty lines
    lines = [line.strip() for line in context.split('\n') if line.strip()]
    return '\n'.join(lines)


def display_rule(rule: Dict, index: int, rule_manager: RuleManager):
    """Display a single rule with formatted context"""
    with st.expander(f"Rule {index + 1}: {rule['title']}", expanded=False):
        # Create columns for better layout
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown("### Context")
            # Check if we're editing this rule
            if st.session_state.editing_rule == index:
                # Show editable text area
                new_context = st.text_area(
                    "Edit Rule Context",
                    value=rule['context'],
                    height=300,
                    key=f"edit_context_{index}"
                )

                # Add Save and Cancel buttons
                if st.button("Save", key=f"save_{index}"):
                    result = validate_and_save_rule(new_context, rule_manager, st.session_state.rules, index)
                    if result["success"]:
                        st.session_state.rules = rule_manager.get_rules()
                        st.session_state.editing_rule = None
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.markdown(result["message"], unsafe_allow_html=True)

                if st.button("Cancel", key=f"cancel_{index}"):
                    st.session_state.editing_rule = None
                    st.rerun()
            else:
                # Display context with proper formatting
                formatted_context = format_rule_context(rule['context'])
                st.text_area(
                    "Rule Context",
                    value=formatted_context,
                    height=300,
                    key=f"context_{index}",
                    disabled=True
                )

        with col2:
            st.markdown("### Metadata")
            st.write("Created:", rule.get('created_at', 'N/A'))

            # Only show Edit/Delete buttons when not editing
            if st.session_state.editing_rule != index:
                if st.button("Edit", key=f"edit_{index}"):
                    st.session_state.editing_rule = index
                    st.rerun()

                if st.button("Delete", key=f"delete_{index}"):
                    if rule_manager.delete_rule(index):
                        st.session_state.rules = rule_manager.get_rules()
                        st.rerun()


def main():
    st.set_page_config(page_title="Rule Management System", layout="wide")
    st.title("Rule Management System")

    # Initialize RuleManager instead of direct JSON operations
    rule_manager = RuleManager()

    # Initialize session state
    if 'rules' not in st.session_state:
        st.session_state.rules = rule_manager.get_rules()
    if 'editing_rule' not in st.session_state:
        st.session_state.editing_rule = None

    # Create two columns for layout
    input_col, display_col = st.columns([1, 1])

    with input_col:
        st.subheader("Add New Rule")
        with st.form("rule_input_form"):
            context = st.text_area(
                "Rule Context",
                height=300,
                help="Enter the rule context. Use new lines for better readability."
            )

            submitted = st.form_submit_button("Submit Rule")

            if submitted and context:
                result = validate_and_save_rule(context, rule_manager, st.session_state.rules)
                if result["success"]:
                    st.session_state.rules = rule_manager.get_rules()
                    st.success(result["message"])
                else:
                    st.markdown(result["message"], unsafe_allow_html=True)

    with display_col:
        # Display existing rules
        if st.session_state.rules:
            st.subheader("Existing Rules")
            for idx, rule in enumerate(st.session_state.rules):
                logging.error(f"Rule {idx}: {rule['title']}")
                display_rule(rule, idx, rule_manager)
        else:
            st.info("No rules added yet. Create your first rule using the form on the left.")


def validate_and_save_rule(context: str, rule_manager: RuleManager, existing_rules: List[Dict],
                           index: int = None) -> Dict:
    """
    Validate and save a rule, either as new or updated.

    Args:
        context: The rule context to validate and save
        rule_manager: RuleManager instance
        existing_rules: List of existing rules
        index: Index of rule being edited (None for new rules)

    Returns:
        Dict containing success status and message
    """
    # Generate title
    title = generate_title(context)

    # Create rule object with formatted context
    rule = {
        "title": title,
        "context": format_rule_context(context)
    }

    # For updates, exclude the current rule from validation
    rules_to_check = existing_rules if index is None else [r for i, r in enumerate(existing_rules) if i != index]

    # Validate rule
    validation_result = validate_rule(rule, rules_to_check)
    logging.info(validation_result)

    if validation_result["is_valid"]:
        if index is None:
            # Add new rule
            rule_manager.add_rule(rule, validation_result["rule_id"])
        else:
            # Update existing rule
            rule_manager.update_rule(index, rule)

        return {
            "success": True,
            "message": f"✔️ Rule {'updated' if index is not None else 'saved'} successfully! Title: {title}"
        }
    else:
        # Format validation error details
        details = validation_result['details'].replace('\n', '<br>')
        error_message = f"""
        ❌ Rule validation failed:
        
        ❓**Reason**: {validation_result['message']}
        
        📇**Details**:
        {details}
        """
        return {
            "success": False,
            "message": error_message
        }


if __name__ == "__main__":
    main()
