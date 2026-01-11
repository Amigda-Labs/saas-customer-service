"""
Input extraction utilities for guardrails.

WHY THIS EXISTS:
----------------
When using the OpenAI Agents SDK with Sessions (e.g., SQLiteSession), the SDK 
automatically prepends conversation history to each new input. This means that
guardrails receive the ENTIRE conversation, not just the current message.

THE PROBLEM:
If a user sends an abusive message that triggers a guardrail, then sends a 
normal message like "hello", the guardrail will STILL see the old abusive 
message in the history and keep triggering - even though the new input is fine.

Example of what guardrail receives WITH Sessions:
    [
        {"role": "user", "content": "My name is Bong"},
        {"role": "assistant", "content": "Nice to meet you, Bong!"},
        {"role": "user", "content": "book ALL slots for the week"},  # <-- Old abusive msg
        {"role": "user", "content": "hello"}  # <-- Current innocent msg
    ]

THE SOLUTION:
Extract only the LATEST user message before running guardrail checks.
This ensures each message is evaluated on its own merit, not contaminated
by previous (potentially blocked) messages in the conversation history.

USAGE:
    from guardrails.utils.input_extraction import extract_latest_user_message
    
    @input_guardrail
    async def my_guardrail(ctx, agent, input):
        latest_message = extract_latest_user_message(input)
        # Now check only the latest message
        ...
"""

from agents import TResponseInputItem


def extract_latest_user_message(input: str | list[TResponseInputItem]) -> str:
    """
    Extract only the latest user message from guardrail input.
    
    When using Sessions, the `input` parameter contains the full conversation
    history, not just the current message. This function extracts only the
    most recent user message for isolated evaluation.
    
    Args:
        input: Either a simple string (no session) or a list of conversation
               items (when using SQLiteSession, etc.)
    
    Returns:
        The text content of the most recent user message.
        
    Examples:
        >>> extract_latest_user_message("hello")
        'hello'
        
        >>> extract_latest_user_message([
        ...     {"role": "user", "content": "old message"},
        ...     {"role": "assistant", "content": "response"},
        ...     {"role": "user", "content": "new message"}
        ... ])
        'new message'
    """
    # Simple string input (no session/history)
    if isinstance(input, str):
        return input
    
    # List input (session prepends conversation history)
    if isinstance(input, list):
        # Iterate backwards to find the most recent user message
        for item in reversed(input):
            if isinstance(item, dict) and item.get("role") == "user":
                content = item.get("content", "")
                
                # Content can be a string
                if isinstance(content, str):
                    return content
                
                # Or a list of content blocks (multimodal messages)
                if isinstance(content, list):
                    texts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            texts.append(block.get("text", ""))
                        elif isinstance(block, str):
                            texts.append(block)
                    return " ".join(texts)
    
    # Fallback: convert to string (shouldn't normally reach here)
    return str(input)