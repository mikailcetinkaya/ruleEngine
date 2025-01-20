import logging

from litellm import completion


def generate_title(context):
    """
    Generate a title for the rule using Gemini via LiteLLM
    """
    try:
        prompt = f"""
        Based on the following context, generate a concise and descriptive title (max 10 words):
        
        Context:
        {context}
        
        Generate only the title, nothing else.
        """

        response = completion(
            model="gemini/gemini-1.5-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )

        # Extract the generated title from the response
        title = response.choices[0].message.content.strip()

        # Ensure the title is not too long
        words = title.split()
        if len(words) > 10:
            title = " ".join(words[:10])

        return title

    except Exception as e:
        # In case of any errors, generate a basic title
        logging.error(e)
        return f"Rule - {context[:30]}..."
