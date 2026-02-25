import os
import re
import tempfile
import threading
import shutil
import subprocess
import asyncio
import readline
from time import sleep
import webbrowser
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit
from prompt_toolkit.layout.containers import FloatContainer, Float
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.widgets import TextArea, Frame, Dialog, Button
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style, merge_styles
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import PythonLexer, GoLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.styles.pygments import style_from_pygments_cls


# -----------------------
# Global variables
# -----------------------
file_buffers = {}
open_files = []
file_index = 0
current_file = "untitled.py"
floats = []

syntax_enabled = True

all_themes = [
    "material",
    "lightbulb",
    "zenburn",
    "dracula",
    "coffee"
]

current_theme_index = 0

WHITE  = "\033[1;37m"
YELLOW = "\033[1;33m"
CYAN   = "\033[1;36m"
RED    = "\033[1;31m"
GREEN  = "\033[1;32m"
RESET  = "\033[0m"

# -----------------------
# Utilities
# -----------------------
def load_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except:
        return ""


def save_file(path, content):
    with open(path, "w") as f:
        f.write(content)


def get_theme_style():
    return style_from_pygments_cls(get_style_by_name(all_themes[current_theme_index]))


def goto_bing():
    os.system("w3m bing.com")

# -----------------------
# Styles
# -----------------------
base_style = Style.from_dict(
    {
        "top-pane": "bg:#000000 #ffffff bold",
        "bottom-pane": "bg:#000000 #ffffff bold",
        "status": "bg:#001122 #ffffff bold",
    }
)

style = merge_styles([get_theme_style(), base_style])

def get_lexer():
    if not syntax_enabled:
        return None
    if current_file.endswith(".py"):
        return PygmentsLexer(PythonLexer)
    else:
        return PygmentsLexer(GoLexer)



def editor():
    # -----------------------
    # Editor and Terminal
    # -----------------------



    top_editor = TextArea(
        text="",
        lexer=get_lexer(),
        scrollbar=False,
        line_numbers=False,
        focus_on_click=True,
        wrap_lines=True,
        multiline=True,
        height=Dimension(min=7),
    )

    bottom_editor = TextArea(
        text="",
        scrollbar=False,
        focus_on_click=True,
        wrap_lines=True,
        height=Dimension(min=5),
    )

    status_bar = TextArea(
        text="",
        height=1,
        style="class:status",
        multiline=False,
        focusable=False,
    )


    # -----------------------
    # Status Bar Handling
    # -----------------------
    def update_status_bar(message=None):
        status_bar.text = current_file if not message else message


    async def show_temp_message(msg, delay=2):
        update_status_bar(msg)
        await asyncio.sleep(delay)
        update_status_bar()


    # -----------------------
    # Key Bindings
    # -----------------------
    kb = KeyBindings()


    @kb.add("c-x")
    def cycle_themes(event):
        global current_theme_index, style
        current_theme_index = (current_theme_index + 1) % len(all_themes)
        style = merge_styles([style_from_pygments_cls(get_style_by_name(all_themes[current_theme_index])), base_style])
        top_editor.lexer = get_lexer()
        event.app.style = style
        update_status_bar(f"Theme: {all_themes[current_theme_index]}")


    @kb.add("c-c")
    def toggle_syntax(event):
        global syntax_enabled
        syntax_enabled = not syntax_enabled
        top_editor.lexer = get_lexer() if syntax_enabled else None
        event.app.invalidate()


    @kb.add("c-space")
    def insert_indent(event):
        editor = top_editor if event.app.layout.has_focus(top_editor) else bottom_editor
        editor.buffer.insert_text("    ")


    @kb.add("c-q")
    def quit_app(event):
        for filename in os.listdir("."):
            if os.path.isfile(filename) and "tmp" in filename:
                os.remove(filename)
        event.app.exit()

    @kb.add("c-y")
    def close_current_file(event):
        if not open_files:
            return

        def confirm_close():
            if len(open_files) <= 1:
                event.app.exit()
                return
            global current_file, file_index
            open_files.pop(file_index)
            file_index %= len(open_files)
            current_file = open_files[file_index]
            top_editor.text = load_file(current_file)
            floats.clear()
            event.app.layout.focus(top_editor)
            update_status_bar()

        def cancel_close():
            floats.clear()
            event.app.layout.focus(top_editor)

        dialog = Dialog(
            title="Close File",
            body=TextArea(
                text=f"Close '{current_file}' ??",
                height=1,
                multiline=False,
                focusable=False
            ),
            buttons=[
                Button(text="Yes", handler=confirm_close),
                Button(text="Cancel", handler=cancel_close)
            ],
            width=50,
            modal=True,
        )

        floats.clear()
        floats.append(Float(content=dialog))
        event.app.layout.focus(dialog)

    @kb.add("c-s")
    def save_current(event):
        if current_file:
            file_buffers[current_file] = top_editor.text
            save_file(current_file, top_editor.text)
            asyncio.ensure_future(show_temp_message(f"File: '{current_file}' Saved.", 2))



    @kb.add("c-n")
    def save_as_dialog(event):
        filename_input = TextArea(height=1, multiline=False)

        def save_handler():
            global current_file, file_index
            path = filename_input.text.strip()
            if not path:
                return
            # Save the current top editor text
            with open(path, "w") as f:
                f.write(top_editor.text)
            if current_file:
                file_buffers[current_file] = top_editor.text
            # Update file tracking
            if path not in open_files:
                open_files.append(path)
            file_index = open_files.index(path)
            current_file = path
            top_editor.text = load_file(path)
            top_editor.lexer = get_lexer()
            floats.clear()
            event.app.layout.focus(top_editor)
            update_status_bar(f"Saved As: {current_file}")

        def cancel():
            floats.clear()
            event.app.layout.focus(top_editor)
            update_status_bar()

        dialog = Dialog(
            title="Save As",
            body=filename_input,
            buttons=[Button(text="Save", handler=save_handler), Button(text="Cancel", handler=cancel)],
            width=60,
            modal=True,
        )

        floats.clear()
        floats.append(Float(content=dialog))
        event.app.layout.focus(filename_input)



    @kb.add("c-_")
    def clear_active(event):
        if event.app.layout.has_focus(top_editor):
            top_editor.text = ""
        elif event.app.layout.has_focus(bottom_editor):
            bottom_editor.text = ""
        update_status_bar()



    @kb.add("c-p")
    def list_functions(event):
        text = top_editor.text
        lines = text.splitlines()
        functions = []
        pattern = re.compile(r'^\s*(?:def|func)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')

        for i, line in enumerate(lines, start=1):
            match = pattern.match(line)
            if match:
                func_name = match.group(1)
                functions.append((func_name, i))

        functions.sort(key=lambda x: x[0].lower())

        if functions:
            output = "Functions:\n\n"
            output += "\n".join(f"{name}, {lineno}" for name, lineno in functions)
        else:
            output = "No functions found."

        bottom_editor.text = output




    @kb.add("c-d")
    def format_pylint_output(event):
        text = bottom_editor.text
        lines = text.splitlines()
        results = {}

        score_match = None
        for line in lines:
            score = re.search(r"rated at ([0-9.]+)/10", line)
            if score:
                score_match = score.group(1)
                continue
            m = re.search(r"/.*?:([0-9]+):([0-9]+):\s+([A-Z]\d+):\s+(.*)", line)
            if m:
                lineno, colno, code, msg = m.groups()
                lineno, colno = int(lineno), int(colno)
                if lineno not in results:
                    results[lineno] = []
                results[lineno].append(msg.strip())

        formatted = ["Code Analysis:", "———————————"]
        for lineno in sorted(results.keys()):
            formatted.append(f"> Line : {lineno}, 0 :\n")
            for msg in results[lineno]:
                formatted.append(f"• {msg}")
            formatted.append("———————————")

        if score_match:
            formatted.append(f"\nCode Score: {score_match} / 10")

        bottom_editor.text = "\n".join(formatted)


    @kb.add("c-v")
    def pylint_top_editor(event):
        def run_lint():
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp_file:
                tmp_file.write(top_editor.text)
                tmp_filename = tmp_file.name

            try:
                result = subprocess.run(
                    ["pylint", tmp_filename],
                    capture_output=True,
                    text=True
                )
                bottom_editor.text = result.stdout + "\n" + result.stderr
            except FileNotFoundError:
                bottom_editor.text = "Error: pylint is not installed or not in PATH."
            except Exception as e:
                bottom_editor.text = f"Unexpected error: {e}"
            finally:
                try:
                    os.remove(tmp_filename)
                except:
                    pass

        threading.Thread(target=run_lint, daemon=True).start()


    @kb.add("c-b")
    def open_shell(event):
        def shell():
            subprocess.run("bash", check=True)
        run_in_terminal(shell)


    @kb.add("c-t")
    def run_code(event):
        def run_script():
            os.system("clear")
            text = top_editor.text
            ext = os.path.splitext(current_file)[1]

            with tempfile.NamedTemporaryFile("w", delete=False, suffix=ext) as tmp:
                tmp.write(text)
                tmp_filename = tmp.name

            try:
                if ext == ".py":
                    os.system(f"python {tmp_filename}")
                elif ext == ".go":
                    os.system(f"go run '{tmp_filename}'")
                elif ext == ".c" or ext == ".rs":
                    bin_path = f"{tmp_filename}.bin"
                    compiler = "gcc" if ext == ".c" else "rustc"
                    os.system(f"{compiler} {tmp_filename} -o {bin_path} && {bin_path}")
                    if os.path.exists(bin_path):
                        os.remove(bin_path)
                else:
                    os.system(f"bash {tmp_filename}")
            finally:
                os.remove(tmp_filename)

            sleep(1)
            input("\n\n\n( Press Enter to return to editor )\n\n")

        run_in_terminal(run_script)



    @kb.add("c-r")
    def run_code(event):
        editor = top_editor if event.app.layout.has_focus(top_editor) else bottom_editor
        ext = os.path.splitext(current_file)[1]

        def run_in_thread():
            with tempfile.NamedTemporaryFile(mode="w", suffix=ext, delete=False) as tmp:
                tmp.write(editor.text)
                tmp_path = tmp.name

            try:
                if ext == ".py":
                    result = subprocess.run(["python3", tmp_path], capture_output=True, text=True)
                elif ext == ".go":
                    result = subprocess.run(["go", "run", tmp_path], capture_output=True, text=True)
                else:
                    result = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="Unsupported file type")

                output = (result.stdout or "") + (result.stderr or "")
                bottom_editor.buffer.insert_text(output)

            finally:
                os.remove(tmp_path)

        threading.Thread(target=run_in_thread, daemon=True).start()


    @kb.add("enter")
    def execute_command(event):
        if event.app.layout.has_focus(bottom_editor):
            buf = bottom_editor.buffer
            line = buf.document.current_line.strip()
            if not line:
                buf.insert_text("\n")
                return
            result = subprocess.run(line, shell=True, capture_output=True, text=True)
            output = (result.stdout or "") + (result.stderr or "")
            buf.insert_text("\n" + output + "\n")
        else:
            event.app.layout.current_control.buffer.newline()


    # -----------------------
    # File Open (Ctrl-F)
    # -----------------------
    @kb.add("c-f")
    def open_file_dialog(event):
        filename_input = TextArea(height=1, multiline=False)

        def open_handler():
            global current_file, file_index
            path = filename_input.text.strip()
            if not path:
                return
            if not os.path.exists(path):
                open(path, "w").close()
            if current_file:
                file_buffers[current_file] = top_editor.text
            if path not in open_files:
                open_files.append(path)
            file_index = open_files.index(path)
            current_file = path
            top_editor.text = load_file(path)
            top_editor.lexer = get_lexer()
            floats.clear()
            event.app.layout.focus(top_editor)
            update_status_bar()

        def cancel():
            floats.clear()
            event.app.layout.focus(top_editor)
            update_status_bar()

        dialog = Dialog(
            title="Open File",
            body=filename_input,
            buttons=[Button(text="Open", handler=open_handler), Button(text="Cancel", handler=cancel)],
            width=60,
            modal=True,
        )

        floats.clear()
        floats.append(Float(content=dialog))
        event.app.layout.focus(filename_input)


    # -----------------------
    # Cycle Files (Ctrl-Z)
    # -----------------------
    @kb.add("c-z")
    def cycle_files(event):
        global file_index, current_file
        if not open_files:
            return
        file_buffers[current_file] = top_editor.text
        file_index = (file_index + 1) % len(open_files)
        current_file = open_files[file_index]
        top_editor.text = load_file(current_file)
        update_status_bar()


    #------------
    # Go to line number
    #-------------


    @kb.add("c-l")
    def goto_line_dialog(event):
        line_input = TextArea(height=1, multiline=False, prompt="Line #: ")

        def jump():
            try:
                line_number = int(line_input.text.strip())
                lines = top_editor.text.splitlines()
                if 1 <= line_number <= len(lines):
                    pos = sum(len(l) + 1 for l in lines[: line_number - 1])
                    top_editor.buffer.cursor_position = pos
            except:
                pass
            floats.clear()
            event.app.layout.focus(top_editor)

        def cancel():
            floats.clear()
            event.app.layout.focus(top_editor)

        dialog = Dialog(
            title="Go To Line",
            body=line_input,
            buttons=[Button(text="Go", handler=jump), Button(text="Cancel", handler=cancel)],
            width=40,
            modal=True,
        )

        floats.clear()
        floats.append(Float(content=dialog))
        event.app.layout.focus(line_input)


    # -----------------------
    # Search (Ctrl-G)
    # -----------------------
    @kb.add("c-g")
    def search_from_cursor(event):
        search_input = TextArea(height=1, multiline=False)

        def do_search():
            term = search_input.text.strip()
            if not term:
                floats.clear()
                event.app.layout.focus(top_editor)
                return

            buf = top_editor.buffer
            start = buf.cursor_position
            found_index = buf.document.text.find(term, start)
            if found_index != -1:
                buf.cursor_position = found_index
                buf.selection_state = None
            floats.clear()
            event.app.layout.focus(top_editor)

        def cancel():
            floats.clear()
            event.app.layout.focus(top_editor)

        dialog = Dialog(
            title="Search",
            body=search_input,
            buttons=[Button(text="Find", handler=do_search), Button(text="Cancel", handler=cancel)],
            width=60,
            modal=True,
        )

        floats.clear()
        floats.append(Float(content=dialog))
        event.app.layout.focus(search_input)


    # -----------------------
    # Root Container & App
    # -----------------------
    divider = TextArea(height=1, text="─" * 80, style="class:bottom-pane", focusable=False)

    root_container = FloatContainer(
        content=HSplit(
            [
                top_editor,
                divider,
                bottom_editor,
                status_bar,
            ]
        ),
        floats=floats,
    )

    app = Application(
        layout=Layout(root_container),
        key_bindings=kb,
        full_screen=True,
        mouse_support=True,
        style=style,
    )



    # -----------------------
    # Startup File Prompt
    # -----------------------
    def prompt_start_file():
        global current_file
        path = input("File: ").strip()
        if not path:
            path = "untitled.py"
        if not os.path.exists(path):
            open(path, "w").close()
        global current_file, file_index
        current_file = path
        open_files.append(path)
        file_index = 0
        top_editor.text = load_file(path)
        update_status_bar()
        current_file = path


    prompt_start_file()
    app.run()


while True:
    command = input(f"\n{CYAN}$ {YELLOW}").strip()

    if "edit" in command:
        editor()
    if "bing" or "web" in command:
        goto_bing()

    try:
        os.system(f"{command}")

    except:
        pass