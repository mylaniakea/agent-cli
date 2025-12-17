from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.shortcuts import CompleteStyle

completer_dict = {"/": {"help": None, "model": {"gpt-4": None, "claude-3": None}, "exit": None}}

session = PromptSession(
    completer=NestedCompleter.from_nested_dict(completer_dict),
    complete_while_typing=True,
    complete_style=CompleteStyle.MULTI_COLUMN,
)

print("Type /h and press Tab. Type /m and press Tab.")
try:
    while True:
        text = session.prompt("Test> ")
        print(f"You typed: {text}")
        if text == "/exit":
            break
except KeyboardInterrupt:
    pass
