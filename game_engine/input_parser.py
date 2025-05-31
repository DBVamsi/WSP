from typing import Dict, List, Optional, Union

def parse_input(raw_text: str) -> Dict[str, Union[Optional[str], List[str]]]:
    """
    Parses the raw text input from the player, normalizing it and splitting
    it into a command and arguments.

    Args:
        raw_text (str): The raw text input from the player.

    Returns:
        Dict[str, Union[Optional[str], List[str]]]: A dictionary containing the
        command (str or None if input is empty) and arguments (list of str).
    """
    normalized_text = raw_text.lower().strip()

    if not normalized_text:
        return {"command": None, "arguments": []}

    words = normalized_text.split()
    command = words[0]
    arguments = words[1:]

    return {"command": command, "arguments": arguments}

if __name__ == '__main__':
    test_inputs = [
        "  Look   AROUND  ",
        "take Potion",
        "attack",
        "   ",
        "go north",
        "EXAMINE map",
        "",
        "  use item key  "
    ]

    for text_input in test_inputs:
        parsed_output = parse_input(text_input)
        print(f"Input: '{text_input}' -> Parsed: {parsed_output}")
