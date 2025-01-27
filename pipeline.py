import json
from typing import List, Dict

import streamlit as st


class PromptChain:
    def __init__(self):
        self.steps = []
        self.rules = {}

    def add_step(self, prompt: str):
        self.steps.append(prompt)

    def add_rule(self, rule_name: str, rule_content: str):
        self.rules[rule_name] = rule_content

    def get_chain(self) -> List[str]:
        return self.steps

    def get_rules(self) -> Dict[str, str]:
        return self.rules

    def clear(self):
        self.steps = []
        self.rules = {}


def save_chain(chain: PromptChain, filename: str):
    data = {
        "steps": chain.get_chain(),
        "rules": chain.get_rules()
    }
    with open(filename, 'w') as f:
        json.dump(data, f)


def load_chain(filename: str) -> PromptChain:
    chain = PromptChain()
    with open(filename, 'r') as f:
        data = json.load(f)
        for step in data["steps"]:
            chain.add_step(step)
        for rule_name, rule_content in data["rules"].items():
            chain.add_rule(rule_name, rule_content)
    return chain


# Initialize session state
if 'chain' not in st.session_state:
    st.session_state.chain = PromptChain()


def main():
    st.title("Prompt Chain Builder")

    # Sidebar for adding steps and rules
    with st.sidebar:
        st.header("Add New Elements")

        # Add new prompt step
        new_prompt = st.text_area("Enter new prompt step:")
        if st.button("Add Prompt Step"):
            if new_prompt:
                st.session_state.chain.add_step(new_prompt)
                st.success("Prompt step added!")

        # Add new rule
        st.header("Add New Rule")
        rule_name = st.text_input("Rule name:")
        rule_content = st.text_area("Rule content:")
        if st.button("Add Rule"):
            if rule_name and rule_content:
                st.session_state.chain.add_rule(rule_name, rule_content)
                st.success("Rule added!")

        # Save and load functionality
        st.header("Save/Load Chain")
        save_filename = st.text_input("Filename to save:", "chain.json")
        if st.button("Save Chain"):
            save_chain(st.session_state.chain, save_filename)
            st.success(f"Chain saved to {save_filename}")

        load_filename = st.text_input("Filename to load:", "chain.json")
        if st.button("Load Chain"):
            try:
                st.session_state.chain = load_chain(load_filename)
                st.success(f"Chain loaded from {load_filename}")
            except FileNotFoundError:
                st.error("File not found!")

        if st.button("Clear Chain"):
            st.session_state.chain.clear()
            st.success("Chain cleared!")

    # Main area to display current chain and rules
    st.header("Current Prompt Chain")
    steps = st.session_state.chain.get_chain()
    if steps:
        for i, step in enumerate(steps, 1):
            st.text_area(f"Step {i}", step, height=100, key=f"step_{i}")
    else:
        st.info("No steps in the chain yet.")

    st.header("Current Rules")
    rules = st.session_state.chain.get_rules()
    if rules:
        for rule_name, rule_content in rules.items():
            st.subheader(rule_name)
            st.text_area("Rule content", rule_content, height=100, key=f"rule_{rule_name}")
    else:
        st.info("No rules defined yet.")

    # Execute chain
    st.header("Execute Chain")
    if st.button("Run Chain"):
        if steps:
            st.write("Executing prompt chain...")
            # Here you would typically integrate with an LLM API
            # For demonstration, we'll just show the steps in sequence
            for i, step in enumerate(steps, 1):
                st.write(f"Step {i}:")
                st.write(step)
                st.write("---")
        else:
            st.warning("No steps to execute!")


if __name__ == "__main__":
    main()
