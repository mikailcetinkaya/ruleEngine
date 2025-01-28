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
                    # Generate new title for edited context
                    new_title = generate_title(new_context)
                    updated_rule = {
                        "title": new_title,
                        "context": format_rule_context(new_context)
                    }

                    # Get all rules except the one being edited
                    current_rules = [r for i, r in enumerate(st.session_state.rules) if i != index]

                    # Validate the updated rule
                    validation_result = validate_rule(updated_rule, current_rules)
                    logging.info(validation_result)
                    if validation_result["is_valid"]:
                        # Update the rule
                        if rule_manager.update_rule(index, updated_rule):
                            st.session_state.rules = rule_manager.get_rules()
                            st.session_state.editing_rule = None
                            st.success("Rule updated successfully!")
                            st.rerun()
                    else:
                        # Format the validation details with proper line breaks
                        details = validation_result['details'].replace('\n', '<br>')
                        error_message = f"""
                        ❌ Rule validation failed:
                        
                        **Reason**: {validation_result['message']}
                        
                        **Details**:
                        {details}
                        """
                        st.markdown(error_message, unsafe_allow_html=True)

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
                # Generate title using Gemini
                title = generate_title(context)

                # Create rule object with formatted context
                new_rule = {
                    "title": title,
                    "context": format_rule_context(context)
                }

                # Validate rule against existing rules
                validation_result = validate_rule(new_rule, st.session_state.rules)
                logging.info(validation_result)
                if validation_result["is_valid"]:
                    st.session_state.rules.append(new_rule)
                    rule_manager.add_rule(new_rule, validation_result["rule_id"])
                    st.success(f"Rule saved successfully! Generated title: {title}")
                else:
                    # Format the validation details with proper line breaks
                    details = validation_result['details'].replace('\n', '<br>')
                    error_message = f"""
                    ❌ Rule validation failed:
                    
                    **Reason**: {validation_result['message']}
                    
                    **Details**:
                    {details}
                    """
                    st.markdown(error_message, unsafe_allow_html=True)

    with display_col:
        # Display existing rules
        if st.session_state.rules:
            st.subheader("Existing Rules")
            for idx, rule in enumerate(st.session_state.rules):
                logging.error(f"Rule {idx}: {rule['title']}")
                display_rule(rule, idx, rule_manager)
        else:
            st.info("No rules added yet. Create your first rule using the form on the left.")

if __name__ == "__main__":
    main()
