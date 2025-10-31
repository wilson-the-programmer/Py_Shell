""" Command Line Interface """
import tempfile
import subprocess
import os
import re
import threading
import random
from time import sleep

from pyfiglet import Figlet

from simple_term_menu import TerminalMenu

from prompt_toolkit import Application

from prompt_toolkit.layout import Layout, HSplit, Window, FloatContainer, Float

from prompt_toolkit.widgets import TextArea, Dialog, Label, Button

from prompt_toolkit.key_binding import KeyBindings

from prompt_toolkit.lexers import PygmentsLexer

from prompt_toolkit.styles import style_from_pygments_cls, merge_styles, Style

from pygments.lexers import BashLexer, CLexer, CppLexer, PythonLexer

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

from rich.console import Console
from rich.syntax import Syntax


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


my_themes = [
    "coffee",
    "dracula",
    "github-dark",
    "gruvbox-dark",
    "lightbulb",
    "material",
    "nord-darker",
    "paraiso-dark",
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
                else:
                        pass
        except:
                        pass





# File Browser
def browse_files(directory="/storage/emulated/0", extensions=(".py", ".c", ".cpp", ".txt"), page_size=15):
    history = []
    os.system("clear")
    while True:
        if not os.path.exists(directory):
            console.print(f"[red]Directory not found:[/red] {directory}")
            return
        all_items = os.listdir(directory)
        all_items.sort()
        files = [f for f in all_items if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith(extensions)]
        folders = [f for f in all_items if os.path.isdir(os.path.join(directory, f))]
        entries = folders + files
        total_pages = (len(entries) - 1) // page_size + 1
        page = 0
        while True:
            start = page * page_size
            end = start + page_size
            page_entries = entries[start:end]
            menu_options = page_entries + [f"[ NEXT PAGE ] →", "[ PREVIOUS PAGE ] ←", "[ BACK ]", "[ RUN ]", "[ EXIT ]"]
            menu = TerminalMenu(menu_options, multi_select=False)
            choice = menu.show()
            if choice is None:
                return
            selection = menu_options[choice]
            if selection == "[ NEXT PAGE ] →":
                if page < total_pages - 1:
                    page += 1
                continue
            elif selection == "[ PREVIOUS PAGE ] ←":
                page = max(0, page - 1)
                continue
            elif selection == "[ DELETE ]":
                file = input("File To Delete: ")
                os.system(f"rm {file}")
                print(f"File '{file}' deleted.")
                sleep(2)
                continue
            elif selection == "[ FILE OPTIONS ]":
                try:
                        os.system("clear")
                        print(f"\n {YELLOW} --[ Choose ]--{RESET}\n\n {CYAN} 1) Edit{RESET}\n {quick_term_color(200,200,200)} 2) Copy\n {quick_term_color(189, 120, 110)} 3) New\n  {quick_term_color(222, 14, 50)}4) Delete\n{quick_term_color(189, 120, 110)}  5) Back\n{quick_term_color(184, 247, 65)}  6) Quick View\n{quick_term_color(252, 150, 20)}  7) Search [substring]\n{quick_term_color(92, 120, 232)}  8) Run Program (.c, .cpp, .py )\n{quick_term_color(188, 53, 248)}  9) System Command\n")

                        choice = input("\n Decision: ")
                        if choice and choice != '5' and choice != '7' and choice != '10':
                                file = session.prompt([('class:cyan bold', "\n\n File: ")])
                        if choice == '1':
                                Vim(file)
                                sleep(1)
                                continue
                        elif choice == '2':
                                os.system(f"cp {file} copy_{file}")
                                sleep(1)
                                print(f"\n\n '{file}' Copy Saved as: 'copy_{file}'")
                                sleep(2)
                                input("\n\n  Press <Return> to Continue  ")
                                continue
                        elif choice == '3':
                                sleep(0.5)
                                print(f"\n\n Opening: '{file}' ...")
                                sleep(1)
                                Vim(file)
                        elif choice == '4':
                                os.system(f"rm {file}")
                                sleep(1)
                                print(f"\n\n File: '{file}' Deleted.")
                                sleep(2)
                                input("\n\n  Press <Return> to Continue  ")
                                continue
                        elif choice == '5':
                                continue
                        elif choice == '6':
                                sleep(1)
                                os.system("clear")
                                sleep(1)
                                os.system(f"cat {file}")
                                sleep(2)
                                edit_choice = input(f"\n\n  Edit: '{file}'  ?\n\n    1) Yes\n    2) No\n\n Decision: ")
                                if edit_choice == '1':
                                    sleep(1)
                                    Vim(file)
                        elif choice == '7':
                                sleep(1)
                                os.system("clear")
                                while True:
                                    searched_string = input("\n\nSearch [Sub]string: , e.g.→ .c, sys, etc.\n\n : ")
                                    if searched_string == 'q' or searched_string == 'exit':
                                    os.system("clear")
                                    browse_files()
                                    sleep(1)
                                    print("\n-----------------------------\n\n")
                                    os.system(f"ls *{searched_string}*")
                                    sleep(2)
                                    try:
                                    file = input("\n\n File to Edit: ")
                                    Vim(file)
                                    except:
                                    pass
                                    sleep(0.6)
                                    input("\n\n  Press <Return> to Continue  ")
                                    continue

                        elif choice == '8':
                                os.system("clear")
                                run_program(file)
                                sleep(1)
                                input("\n\n  Press <Return> to Continue  ")
                                os.system("clear")

                        elif choice == '9':
                                sleep(1)
                                while 1:
                                    command = input(f"{CYAN}\n $ ").strip()
                                    os.system(command)
                                    sleep(0.6)
                                    if command == 'q' or command == 'exit':
                                    clear_terminal()
                                    browse_files()




                except:
                        pass
            elif selection == "[ EXIT ]":
                return "break"
            elif selection == "[ BACK ]":
                if history:
                    directory = history.pop()
                    break
                else:
                    console.print("[yellow]No previous directory.[/yellow]")
                    continue
            else:
                path = os.path.join(directory, selection)
                if os.path.isdir(path):
                    history.append(directory)
                    directory = path
                    break
                else:
                    result = Vim(path)
                    if result == 'browse':
                        continue
                    return




def cpp_lint(file):
    if not os.path.isfile(file):
        print(f"\nFile not found: {file}")
        return

    RED_BOLD = "\033[1;31m"
    GREEN_BOLD = "\033[1;32m"
    YELLOW_BOLD = "\033[1;33m"

    CYAN_BOLD = "\033[1;36m"
    ORANGE = "\033[38;5;214m"
    RESET = "\033[0m"

    # First, compile with g++ -Wall and print output if there are errors
    compile_cmd = ["g++", "-Wall", file]
    compile_proc = subprocess.run(compile_cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if compile_proc.returncode != 0:
        print(f"Compilation Errors:\n{RED_BOLD}--------------------------{RESET}\n")
        print(compile_proc.stdout)
        print(f"{RED_BOLD}--------------------------\n{GREEN_BOLD}")

    # Run cpplint and capture output in a temp file
    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        tmp_filename = tmp.name

    try:
        subprocess.run(["cpplint", file], stdout=open(tmp_filename, "w"), stderr=subprocess.STDOUT, text=True)

        with open(tmp_filename) as f:
            text = f.read()

        lines = text.splitlines()
        cpplint_lines = [line for line in lines if line.strip() and "Done processing" not in line]

        # Extract total cpplint errors
        total_errors = ""
        for line in cpplint_lines:
            if line.startswith("Total errors found:"):
                total_errors = line.replace("Total errors found:", "Errors:").strip()
                break

        pattern = re.compile(r'^(.*?):(\d+):\s*(.*)\s+\[\w+/\w+\]\s+\[(\d)\]$')
        errors_by_file_line = {}

        for line in cpplint_lines:
            match = pattern.match(line)
            if match:
                filename_match, lineno, message, severity = match.groups()
                key = (filename_match, lineno)
                if key not in errors_by_file_line:
                    errors_by_file_line[key] = []

                errors_by_file_line[key].append(f"{message}")

        # Build formatted output for cpplint
        result = []
        files = sorted(set(f for f, _ in errors_by_file_line.keys()))
        for filename in files:
            result.append(f'"{filename}" - {total_errors}\n')
            for key in sorted(errors_by_file_line.keys()):
                f_key, lineno = key
                if f_key != filename:
                    continue
                result.append(f"{CYAN_BOLD}Line {lineno}:{RESET}\n")
                for msg in errors_by_file_line[key]:

                    result.append(f"{YELLOW_BOLD}•{RESET} {msg}")
                result.append("\n🔲🔲🔲 🔲🔲 🔲🔲🔲🔲🔲🔲🔲 🔲🔲 🔲\n")

        if result:
            print("\n".join(result))

    finally:
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)






def Vim(file="new.py"):
    if not os.path.exists(file):
        open(file, 'w').close()

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
        elif file.endswith(".sh"):
            return PygmentsLexer(BashLexer)
        else:
            return PygmentsLexer(PythonLexer)

    style = style_from_pygments_cls(get_style_by_name(my_themes[current_theme_index]))

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

            if any(x in text for x in ["<iostream>", "cout <<"]):
                ext = ".cpp"
            elif any(x in text for x in ["<stdio.h>", "<stdlib.h>", "printf("]):
                ext = ".c"
            elif any(x in text for x in ["import ", "print("]):
                ext = ".py"
            else:
                ext = ".py"

            with tempfile.NamedTemporaryFile("w", delete=False, suffix=ext) as tmp:
                tmp.write(text)
                tmp_filename = tmp.name

            try:
                if ext == ".py":
                    cmd = f"python {tmp_filename}"
                elif ext == ".c":
                    exe = tmp_filename[:-2] + "_exe"
                    os.system(f"gcc {tmp_filename} -o {exe}")
                    cmd = exe
                elif ext == ".cpp":
                    exe = tmp_filename[:-4] + "_exe"
                    os.system(f"g++ {tmp_filename} -o {exe}")
                    cmd = exe
                else:
                    cmd = f"python {tmp_filename}"

                os.system(cmd)
            finally:
                os.remove(tmp_filename)
                if ext in [".c", ".cpp"] and os.path.exists(exe):
                    os.remove(exe)
            sleep(1)
            cyan = "\033[1;36m"
            reset = "\033[0m"
            white = "\033[1;37m"

            input(f"{'\n' * 10}{cyan}[Press Enter to return to editor]{white}")

        run_in_terminal(run_script)
        status_message["text"] = "▶ Code executed (unsaved)"
        clear_status_after_delay()

    @kb.add("c-g")
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
        current_theme_index = (current_theme_index + 1) % len(my_themes)
        style = style_from_pygments_cls(get_style_by_name(my_themes[current_theme_index]))
        editor.lexer = get_lexer()
        event.app.style = style
        status_message["text"] = f"Theme: {my_themes[current_theme_index]}"
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
        style = style_from_pygments_cls(get_style_by_name("lightbulb"))


    root_container = FloatContainer(
        content=HSplit([editor, status_bar]),
        floats=floats
    )

    layout = Layout(root_container)

    app = Application(
        layout=layout,
        key_bindings=kb,
        full_screen=True,
        style=style
    )

    app.run()






fig = Figlet(font='doom')
print(fig.renderText("PyShell"))
sleep(0.8)

print("\n🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲🔲\n")



HOME_DIR = '/storage/emulated/0'
history_file = os.path.expanduser('~/.my_prompt_history')

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
        if not command:
            continue

        if command == "k":
            os.system('clear')

        elif command in ("math", "mathomatic"):
            mathomatic()

        elif command.startswith("run "):
            file = command[4:].strip()
            run_program(file)

        elif command.startswith(("vim ", "edit ")):
            file = command.split(' ', 1)[1].strip()
            Vim(file)

        elif command in ("vim", "edit", "nano"):
            Vim()

        elif command.startswith("cpp_lint "):
            file = command[9:].strip()
            cpp_lint(file)

        elif command.startswith("ls*"):
            files = command[4:].strip()
            os.system(f"ls *{files}*")

        elif command == "files":
            browse_files()

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

        else:
            os.system(command)

    except (KeyboardInterrupt, EOFError):
        break
    except Exception:
        pass


     