import readline
import os
import codeop
import tempfile
from time import sleep
                                           from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.styles.pygments import style_from_pygments_cls

current_theme_name = "material"
current_style = style_from_pygments_cls(get_style_by_name(current_theme_name))

session = PromptSession(
    lexer=PygmentsLexer(PythonLexer),
    style=current_style
)

compiler = codeop.compile_command
buffer = []
local_env = {}
empty_commands = 0

WHITE = "\033[1;38;2;255;255;255m"
YELLOW = "\033[1;38;2;255;255;0m"
ORANGE = "\033[1;38;2;255;165;0m"
CYAN = "\033[1;38;2;0;255;255m"
GREY = "\033[1;38;2;190;190;190m"
RESET = "\033[0m"

os.system("clear")

print(f"\n\n{ORANGE}======[{CYAN} Ipython {YELLOW}Plus {ORANGE}]======{RESET}\n\n\n")
sleep(1)

while True:
    try:
        prompt_text = ">>> " if not buffer else "..."
        line = session.prompt(prompt_text)

        cmd = line.strip()

        if cmd.startswith("%cmd"):
            parts = cmd.split(maxsplit=1)

            if len(parts) == 2:
                os.system(parts[1])
            else:
                print("Usage: %cmd <command>")

            continue

        if cmd == "bash":
            os.system("bash")
            continue

        if cmd == "q":
            break

        if cmd.startswith("%view") or cmd.startswith("%cat"):
            parts = cmd.split(maxsplit=1)
            if len(parts) == 2:
                filename = parts[1].strip()
                os.system(f"cat '{filename}'")
            continue

        if cmd.startswith("%edit") or cmd.startswith("%nano"):
            parts = cmd.split(maxsplit=1)
            if len(parts) == 2:
                filename = parts[1].strip()
                os.system(f"nano '{filename}'")
            else:
                print("Usage: %edit <filename>")
            continue

        if cmd.startswith("%run"):
            parts = cmd.split(maxsplit=1)
            if len(parts) == 2:
                filename = parts[1].strip()

                filename = os.path.expanduser(filename)
                filename = os.path.abspath(filename)

                if not os.path.exists(filename):
                    print(f"File '{filename}' not found")
                    continue

                ext = filename.split(".")[-1].lower()

                if ext == "py":
                    os.system(f"python3 '{filename}'")

                elif ext == "sh":
                    os.system(f"chmod +x '{filename}' && bash '{filename}'")

                elif ext == "c":
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        exe_name = tmp.name

                    compile_cmd = f"gcc '{filename}' -o '{exe_name}'"
                    run_cmd = f"'{exe_name}'"

                    if os.system(compile_cmd) == 0:
                        os.system(run_cmd)

                    os.remove(exe_name)

                elif ext == "go":
                    os.system(f"go run '{filename}'")

                else:
                    print("Unsupported file type")
            else:
                print("Usage: %run <filename>")
            continue

        buffer.append(line)
        source = "\n".join(buffer)

        if buffer and not line.strip():
            empty_commands += 1
        else:
            empty_commands = 0

        code_obj = compiler(source, "<input>", "single")

        if code_obj is None:
            if empty_commands >= 3:
                print(f"\n\n{CYAN}Multiple Empty lines detected.")
                sleep(1)
                print(f"\n\n{YELLOW}Function Canceled.\n\n")
                sleep(1)
                buffer = []
                empty_commands = 0
            continue

        exec(code_obj, local_env)
        buffer = []
        empty_commands = 0

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
        buffer = []
        empty_commands = 0

    except EOFError:
        print("\nExiting")
        break

    except Exception as e:
        sleep(0.6)
        print(f"\n\n{GREY}{type(e).__name__}: {e}\n\n")
        sleep(0.6)
        buffer = []

