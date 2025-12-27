
import readline

import tempfile
import subprocess
import os
import re
import shutil
import threading
import random
from time import sleep
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, Window, FloatContainer, Float
from prompt_toolkit.widgets import TextArea, Dialog, Label, Button
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import style_from_pygments_cls, merge_styles, Style
from pygments.lexers import BashLexer, CLexer, CppLexer, PythonLexer, JavaLexer, JavascriptLexer, RustLexer
from pygments.styles import get_style_by_name
from pygments.styles import get_all_styles
from pygments.style import Style as PygmentsStyle
from pygments.token import Token, Keyword, Name, Comment, String, Number, Operator, Generic
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.key_binding.bindings.focus import focus_next
from prompt_toolkit.completion import WordCompleter, Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit import PromptSession

all_themes = [
    "abap","algol","algol_nu","arduino","autumn",
    "bw","borland","coffee","colorful","default",
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




def editor(file="test.py"):

    if not file:
        file = "test.py"
    last_file = None
    file_buffers = {}
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
        elif file.endswith(".js"):
            return PygmentsLexer(JavascriptLexer)
        elif file.endswith(".java"):
            return PygmentsLexer(JavaLexer)
        elif file.endswith(".sh"):
            return PygmentsLexer(BashLexer)
        else:
            return PygmentsLexer(PythonLexer)

    style = style_from_pygments_cls(get_style_by_name(all_themes[current_theme_index]))

    editor = TextArea(
        text=current_text,
        lexer=get_lexer(),
        scrollbar=False,
        line_numbers=True,
        multiline=True,
        wrap_lines=True,
        focus_on_click=True
    )
    status_bar = Window(
        height=1,
        content=FormattedTextControl(get_status),
        style="class:status"
    )
    kb = KeyBindings()
    floats = []
    def clear_status_after_delay(seconds=2):
        def clear():
            status_message["text"] = f"Editing: {file}"
        threading.Timer(seconds, clear).start()

    @kb.add("c-space")
    def _(event):
        event.app.current_buffer.insert_text("    ")

    @kb.add("c-s")
    def save(event):
        with open(file, 'w') as f:
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
                    os.system(f"python {tmp_filename}")
                elif file.endswith(".js"):
                    os.system(f"node {tmp_filename}")
                elif file.endswith(".c"):
                    # 1. Define a specific name for the binary
                    bin_path = f"{tmp_filename}.bin"
                    
                    # 2. Use gcc for C files
                    # -o ensures we don't leave 'a.out' behind
                    os.system(f"gcc {tmp_filename} -o {bin_path} && {bin_path}")
                    
                    # 3. Clean up the binary immediately
                    if os.path.exists(bin_path):
                        os.remove(bin_path)
                elif file.endswith(".cpp"):
                    # 1. Define a specific name for the binary
                    bin_path = f"{tmp_filename}.bin"
                    
                    # 2. Compile with -o to avoid creating 'a.out'
                    # Use '&&' so it only runs if compilation succeeds
                    os.system(f"g++ {tmp_filename} -o {bin_path} && {bin_path}")
                    
                    # 3. Clean up the binary immediately after running
                    if os.path.exists(bin_path):
                        os.remove(bin_path)

                elif file.endswith(".rs"):
                    # 1. Define the binary name clearly
                    bin_path = f"{tmp_filename}.bin"
                    
                    # 2. Compile and then execute using the full path
                    # We remove the './' and let the shell use the full path
                    os.system(f"rustc {tmp_filename} -o {bin_path} && {bin_path}")
                    
                    # 3. Clean up the binary
                    if os.path.exists(bin_path):
                        os.remove(bin_path)

                elif ext == ".java":
                    match = re.search(r'public\s+class\s+(\w+)', editor.text)
                    cls_name = match.group(1) if match else "Main"
                    tmp_dir = tempfile.mkdtemp()
                    tmp_java = os.path.join(tmp_dir, f"{cls_name}.java")
                    with open(tmp_java, "w", encoding="utf-8") as f:
                        f.write(editor.text)
                    compile_proc = subprocess.run(["javac", tmp_java], capture_output=True, text=True)
                    if compile_proc.returncode != 0:
                        print(compile_proc.stderr)
                    else:
                        subprocess.run(["java", "-cp", tmp_dir, cls_name], text=True)

                    shutil.rmtree(tmp_dir)

                else:
                    os.system(f"bash {tmp_filename}")
            finally:
                os.remove(tmp_filename)
            sleep(1)
            cyan = "\033[1;36m"
            reset = "\033[0m"
            white = "\033[1;37m"
            input("\n\n\n( Press Enter to return to editor )\n\n")
        run_in_terminal(run_script)
        status_message["text"] = "▶ Code executed (unsaved)"

        clear_status_after_delay()
    @kb.add("c-f")
    def open_new_file(event):
        nonlocal file, last_file
        filename_input = TextArea(height=1, prompt='File: ', multiline=False)
        def ok_handler():
            nonlocal file, last_file
            new_path = filename_input.text.strip()
            if new_path:
                file_buffers[file] = editor.text
                if not os.path.exists(new_path):
                    open(new_path, 'w').close()
                last_file = file
                file = new_path
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
                Button(text="Cancel", handler=cancel_handler)
            ],
            width=60,
            modal=True
        )
        floats.clear()
        floats.append(Float(content=file_dialog))
        app.layout.focus(filename_input)
    @kb.add("c-z")
    def toggle_files(event):
        nonlocal file, last_file
        if last_file:
            file_buffers[file] = editor.text
            file, last_file = last_file, file
            editor.text = file_buffers.get(file, load_file(file))
            status_message["text"] = f"Switched to: {file}"
            clear_status_after_delay()
    @kb.add("c-l")
    def goto_line(event):
        line_input = TextArea(height=1, prompt='Line #: ', multiline=False)
        def jump():
            try:
                line_number = int(line_input.text.strip())
                lines = editor.text.splitlines()
                if 1 <= line_number <= len(lines):
                    pos = sum(len(l) + 1 for l in lines[:line_number - 1])
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
                Button(text="Cancel", handler=cancel)
            ],
            width=50,
            modal=True
        )
        floats.clear()
        floats.append(Float(content=goto_dialog))
        app.layout.focus(line_input)

    @kb.add("c-x")
    def cycle_theme(event):
        nonlocal current_theme_index, style, syntax_enabled
        syntax_enabled = True
        current_theme_index = (current_theme_index + 1) % len(all_themes)
        style = style_from_pygments_cls(get_style_by_name(all_themes[current_theme_index]))
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
    if file.endswith(".py"):
    	style = style_from_pygments_cls(get_style_by_name("material"))
    elif file.endswith(".sh"):
    	style = style_from_pygments_cls(get_style_by_name("coffee"))
    else:
    	style = style_from_pygments_cls(get_style_by_name("material"))

    root_container = FloatContainer(
        content=HSplit([editor, status_bar]),
        floats=floats
    )
    layout = Layout(root_container)
    app = Application(
        layout=layout,
        key_bindings=kb,
        full_screen=True,
        style=style,
        mouse_support=True
    )
    app.run()


class PathCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.strip()
        if not text:
            return
        parts = text.split()
        last = parts[-1] if parts else ''
        dirname, prefix = os.path.split(last)
        dirname = dirname or '.'
        try:
            for name in os.listdir(dirname):
                if name.startswith(prefix):
                    path = os.path.join(dirname, name)
                    display = name + ('/' if os.path.isdir(path) else '')
                    yield Completion(display, start_position=-len(prefix))
        except Exception:
            pass

HOME_DIR = "/home/wilsony175"
history_file = os.path.expanduser('~/.my_prompt_history')

session = PromptSession(
    auto_suggest=AutoSuggestFromHistory(),
    history=FileHistory(history_file),
    completer=PathCompleter()
)



while True:
    prompt_label = "\n$ "
    try:
        colors = ["cyan", "yellow", "white", "orange", "lightblue", "lightgreen", "lightgrey"]
        prompt_color = random.choice(colors)
        command = session.prompt([(f'class:{prompt_color} bold', prompt_label)]).strip()
        os.system(command)

        if not command:
            continue

        if command.startswith("edit "):
            file = command[5:]
            editor(file)

        elif command == "cd":
            os.chdir(HOME_DIR)
            os.system('pwd')

        elif command.startswith("cd"):
            new_path = command[2:].strip()
            if new_path in ("", "~", "~/"):
                new_path = HOME_DIR
            else:
                if new_path.startswith("~/"):
                    new_path = new_path.replace("~", HOME_DIR, 1)
                new_path = os.path.abspath(os.path.expanduser(new_path))
            os.chdir(new_path)
            os.system('pwd')

        if command.lower() == "q":
            break
    except Exception as e:
        print(e)

