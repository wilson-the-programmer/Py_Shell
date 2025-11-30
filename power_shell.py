"""Command Line Interface"""

import tempfile
import subprocess
import os
import re
import threading
import random
from time import sleep

from pyfiglet import Figlet

from prompt_toolkit import Application

from prompt_toolkit.layout import Layout, HSplit, Window, FloatContainer, Float

from prompt_toolkit.widgets import TextArea, Dialog, Label, Button

from prompt_toolkit.key_binding import KeyBindings

from prompt_toolkit.lexers import PygmentsLexer

from prompt_toolkit.styles import style_from_pygments_cls, Style

from pygments.lexers import BashLexer, CLexer, CppLexer, PythonLexer, HtmlLexer, JavascriptLexer

from pygments.styles import get_style_by_name

from prompt_toolkit.layout.controls import FormattedTextControl

from prompt_toolkit.application import run_in_terminal

from prompt_toolkit.completion import Completer, Completion

from prompt_toolkit.history import FileHistory

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from prompt_toolkit import PromptSession

all_themes = [
    "abap",
    "algol",
    "algol_nu",
    "arduino",
    "autumn",
    "bw",
    "borland",
    "coffee",
    "colorful",
    "default",
    "dracula",
    "emacs",
    "friendly_grayscale",
    "friendly",
    "fruity",
    "github-dark",
    "gruvbox-dark",
    "gruvbox-light",
    "igor",
    "inkpot",
    "lightbulb",
    "lilypond",
    "lovelace",
    "manni",
    "material",
    "monokai",
    "murphy",
    "native",
    "nord-darker",
    "nord",
    "one-dark",
    "paraiso-dark",
    "paraiso-light",
    "pastie",
    "perldoc",
    "rainbow_dash",
    "rrt",
    "sas",
    "solarized-dark",
    "solarized-light",
    "staroffice",
    "stata-dark",
    "stata-light",
    "tango",
    "trac",
    "vim",
    "vs",
    "xcode",
    "zenburn"
]



BRIGHT_GREEN = "\033[1;92m"
BRIGHT_YELLOW = "\033[1;93m"
BRIGHT_CYAN = "\033[1;96m"
BRIGHT_ORANGE = "\033[1;38;5;208m"
RESET = "\033[0m"


def run_program(file):
    try:
        os.system("clear")
        if file.endswith(".sh"):
            os.system(f"bash {file}")
        elif file.endswith(".c"):
            os.system(f"gcc {file} && ./a.out")
        elif file.endswith(".cpp"):
            os.system(f"g++ {file} && ./a.out")
        elif file.endswith(".py"):
            os.system(f"python {file}")
    except:
        pass


def Vim(file="new.py"):
    if not os.path.exists(file):
        open(file, 'w').close()
    
    file_buffers = {}
    open_files = [file]
    current_file_index = 0

    def load_file(path):
        if not os.path.exists(path):
            open(path, 'w').close()
        with open(path) as f:
            return f.read()

    current_text = load_file(file)
    status_message = {"text": f"Editing: {file}"}

    def get_status():
        return [("class:status", status_message["text"])]

    syntax_enabled = True
    current_theme_index = 0

    def get_lexer():
        if not syntax_enabled:
            return None
        if file.endswith(".py"):
            return PygmentsLexer(PythonLexer)
        elif file.endswith(".c"):
            return PygmentsLexer(CLexer)
        elif file.endswith(".cpp"):
            return PygmentsLexer(CppLexer)
        elif file.endswith(".sh"):
            return PygmentsLexer(BashLexer)
        elif file.endswith(".html"):
            return PygmentsLexer(HtmlLexer)
        elif file.endswith(".js"):
            return PygmentsLexer(JavascriptLexer)

        else:
            return PygmentsLexer(PythonLexer)

    editor = TextArea(
        text=current_text,
        lexer=get_lexer(),
        scrollbar=False,
        line_numbers=True,
        multiline=True,
        wrap_lines=True,
        focus_on_click=True,
    )

    status_bar = Window(
        height=1, content=FormattedTextControl(get_status), style="class:status"
    )

    kb = KeyBindings()
    floats = []

    def clear_status_after_delay(seconds=2):
        def clear():
            status_message["text"] = f"Editing: {file}"

        threading.Timer(seconds, clear).start()

    @kb.add("c-s")
    def save(event):
        with open(file, "w") as f:
            f.write(editor.text)
        file_buffers[file] = editor.text
        status_message["text"] = "✔ Saved!"
        clear_status_after_delay()

    @kb.add("c-r")
    def run_code(event):
        def run_script():
            os.system("clear")
            text = editor.text
            ext = os.path.splitext(file)[1]

            with tempfile.NamedTemporaryFile("w", delete=False, suffix=ext) as tmp:
                tmp.write(text)
                tmp_filename = tmp.name

            try:
                if file.endswith(".py"):
                    cmd = f"python {tmp_filename}"
                    os.system(cmd)
                elif file.endswith(".c"):
                    exe = tmp_filename[:-2] + "_exe"
                    os.system(f"gcc {tmp_filename} -o {exe}")
                    os.system(f"./{exe}")
                elif file.endswith(".cpp"):
                    exe = tmp_filename[:-4] + "_exe"
                    os.system(f"g++ {tmp_filename} -o {exe}")
                    os.system(f"./{exe}")
                elif file.endswith(".js"):
                    cmd = f"node {tmp_filename}"
                    os.system(cmd)

                else:
                    os.system(f"python {tmp_filename}")
            finally:
                os.remove(tmp_filename)
                if ext in [".c", ".cpp"] and os.path.exists(exe):
                    os.remove(exe)
            sleep(1)
            input(f"\n{BRIGHT_CYAN}[Press Enter to return to editor]{RESET}")

        run_in_terminal(run_script)
        status_message["text"] = "▶ Code executed (unsaved)"
        clear_status_after_delay()

    @kb.add("c-f")
    def open_new_file(event):
        nonlocal file, current_file_index

        filename_input = TextArea(height=1, prompt="File: ", multiline=False)

        def ok_handler():
            nonlocal file, current_file_index
            new_path = filename_input.text.strip()
            if new_path:
                file_buffers[file] = editor.text
                if not os.path.exists(new_path):
                    open(new_path, "w").close()
                if new_path not in open_files:
                    open_files.append(new_path)
                current_file_index = open_files.index(new_path)
                file = open_files[current_file_index]
                editor.lexer = get_lexer()
                editor.text = file_buffers.get(file, load_file(file))
                status_message["text"] = f"Opened: {file}"
            floats.clear()
            app.layout.focus(editor)

        def cancel_handler():
            floats.clear()
            app.layout.focus(editor)

        input_kb = KeyBindings()

        @input_kb.add("enter")
        def _(event):
            ok_handler()

        @input_kb.add("escape")
        def _(event):
            cancel_handler()

        filename_input.control.key_bindings = input_kb

        file_dialog = Dialog(
            title="Open File",
            body=HSplit([filename_input]),
            buttons=[
                Button(text="Open", handler=ok_handler),
                Button(text="Cancel", handler=cancel_handler),
            ],
            width=60,
            modal=True,
        )

        floats.clear()
        floats.append(Float(content=file_dialog))
        app.layout.focus(filename_input)

    @kb.add("c-z")
    def toggle_files(event):
        nonlocal file, current_file_index
        if len(open_files) > 1:
            file_buffers[file] = editor.text
            current_file_index = (current_file_index + 1) % len(open_files)
            file = open_files[current_file_index]
            editor.text = file_buffers.get(file, load_file(file))
            status_message["text"] = f"File: '{file}'"
            clear_status_after_delay()

    @kb.add("c-g")
    def goto_line(event):
        line_input = TextArea(height=1, prompt="GoTo Line: ", multiline=False)

        def jump():
            try:
                line_number = int(line_input.text.strip())
                lines = editor.text.splitlines()
                if 1 <= line_number <= len(lines):
                    pos = sum(len(l) + 1 for l in lines[: line_number - 1])
                    editor.buffer.cursor_position = pos
                    status_message["text"] = f"Jumped to line {line_number}"
                else:
                    status_message["text"] = "Invalid line number"
            except:
                status_message["text"] = "Invalid input"
            floats.clear()
            app.layout.focus(editor)
            clear_status_after_delay()

        def cancel():
            floats.clear()
            app.layout.focus(editor)

        input_kb = KeyBindings()

        @input_kb.add("enter")
        def _(event):
            jump()

        @input_kb.add("escape")
        def _(event):
            cancel()

        line_input.control.key_bindings = input_kb

        goto_dialog = Dialog(
            title="Go to Line",
            body=HSplit([line_input]),
            buttons=[
                Button(text="Go", handler=jump),
                Button(text="Cancel", handler=cancel),
            ],
            width=50,
            modal=True,
        )

        floats.clear()
        floats.append(Float(content=goto_dialog))
        app.layout.focus(line_input)

    @kb.add("c-x")
    def cycle_theme(event):
        nonlocal current_theme_index, style, syntax_enabled
        syntax_enabled = True
        current_theme_index = (current_theme_index + 1) % len(all_themes)
        style = style_from_pygments_cls(
            get_style_by_name(all_themes[current_theme_index])
        )
        editor.lexer = get_lexer()
        event.app.style = style
        status_message["text"] = f"Theme: {all_themes[current_theme_index]}"
        clear_status_after_delay()

    @kb.add("c-c")
    def toggle_syntax(event):
        nonlocal syntax_enabled
        syntax_enabled = not syntax_enabled
        editor.lexer = get_lexer()
        if syntax_enabled:
            status_message["text"] = "Syntax highlighting enabled"
        else:
            status_message["text"] = "Syntax highlighting disabled"
        clear_status_after_delay()

    @kb.add("c-q")
    def quit_app(event):
        event.app.exit()

    custom_status_style = Style.from_dict({"status": "bold white bg:#000000"})

    root_container = FloatContainer(content=HSplit([editor, status_bar]), floats=floats)

    layout = Layout(root_container)

    if file.endswith(".py"):
        style = style_from_pygments_cls(get_style_by_name("material"))
    elif file.endswith(".c") or file.endswith(".cpp"):
        style = style_from_pygments_cls(get_style_by_name("lightbulb"))
    elif file.endswith(".sh"):
        style = style_from_pygments_cls(get_style_by_name("coffee"))
    else:
        style = style_from_pygments_cls(get_style_by_name("material"))

    app = Application(
        layout=layout,
        key_bindings=kb,
        full_screen=True,
        style=style,
        mouse_support=True,
    )

    app.run()


fig = Figlet(font="doom")
print(fig.renderText("PyShell"))
sleep(0.8)
print("\n🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲\n")

HOME_DIR = "/storage/emulated/0"
history_file = os.path.expanduser("~/.my_prompt_history")


class PathCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.strip()
        if not text:
            return
        parts = text.split()
        last = parts[-1] if parts else ""
        dirname, prefix = os.path.split(last)
        dirname = dirname or "."
        try:
            for name in os.listdir(dirname):
                if name.startswith(prefix):
                    path = os.path.join(dirname, name)
                    display = name + ("/" if os.path.isdir(path) else "")
                    yield Completion(display, start_position=-len(prefix))
        except Exception:
            pass


session = PromptSession(
    auto_suggest=AutoSuggestFromHistory(),
    history=FileHistory(history_file),
    completer=PathCompleter(),
)

while True:
    prompt_label = "\n$ "
    try:
        colors = [
            "cyan",
            "yellow",
            "white",
            "orange",
            "lightblue",
            "lightgreen",
            "lightgrey",
        ]
        prompt_color = random.choice(colors)
        command = session.prompt([(f"class:{prompt_color} bold", prompt_label)]).strip()
        if not command:
            continue

        if command == "k":
            os.system("clear")

        elif command.startswith("run "):
            file = command[4:].strip()
            run_program(file)

        elif command.startswith(("vim ", "edit ")):
            file = command.split(" ", 1)[1].strip()
            Vim(file)

        elif command in ("vim", "edit", "nano"):
            Vim()

        elif command.startswith("ls*"):
            files = command[4:].strip()
            os.system(f"ls *{files}*")

        elif command == "cd":
            os.chdir(HOME_DIR)
            os.system("pwd")

        elif command.startswith("cd"):
            new_path = command[2:].strip()
            if new_path in ("", "~", "~/"):
                new_path = HOME_DIR
            else:
                if new_path.startswith("~/"):
                    new_path = new_path.replace("~", HOME_DIR, 1)
                new_path = os.path.abspath(os.path.expanduser(new_path))
            os.chdir(new_path)
            os.system("pwd")

        else:
            os.system(command)

    except (KeyboardInterrupt, EOFError):
        break
    except Exception:
        pass
