import os
import RNS
import threading
from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import SearchToolbar, TextArea

sideband = None
application = None
output_document = Document(text="", cursor_position=0)
output_field = None

def attach(target_core):
    global sideband
    sideband = target_core
    RNS.logdest = RNS.LOG_CALLBACK
    RNS.logcall = receive_output
    console()

def parse(uin):
    args = uin.split(" ")
    cmd = args[0]
    if   cmd == "q" or cmd == "quit": quit_action()
    elif cmd == "clear": cmd_clear(args)
    elif cmd == "raw": cmd_raw(args, uin.replace("raw ", ""))
    elif cmd == "log": cmd_log(args)
    else: receive_output(f"Unknown command: {cmd}")

def cmd_clear(args):
    output_document = output_document = Document(text="", cursor_position=0)
    output_field.buffer.document = output_document

def cmd_raw(args, expr):
    if expr != "" and expr != "raw":
        try: receive_output(eval(expr))
        except Exception as e: receive_output(str(e))

def cmd_log(args):
    try:
        if len(args) == 1: receive_output(f"Current loglevel is {RNS.loglevel}")
        else: RNS.loglevel = int(args[1]); receive_output(f"Loglevel set to {RNS.loglevel}")
    except Exception as e:
        receive_output("Invalid loglevel: {e}")

def set_log(level=None):
    if level: RNS.loglevel = level
    if RNS.loglevel == 0: receive_output("Logging squelched. Use log command to print output to console.")

def quit_action():
    receive_output("Shutting down Sideband...")
    sideband.should_persist_data()
    application.exit()

def receive_output(msg):
    global output_document, output_field
    content = f"{output_field.text}\n{msg}"
    output_document = output_document = Document(text=content, cursor_position=len(content))
    output_field.buffer.document = output_document

def console():
    global output_document, output_field, application
    search_field = SearchToolbar()

    output_field = TextArea(style="class:output-field", text="Sideband console ready")
    input_field = TextArea(
        height=1,
        prompt="> ",
        style="class:input-field",
        multiline=False,
        wrap_lines=False,
        search_field=search_field)

    container = HSplit([
        output_field,
        Window(height=1, char="-", style="class:line"),
        input_field,
        search_field])

    def accept(buff): parse(input_field.text)
    input_field.accept_handler = accept

    kb = KeyBindings()
    @kb.add("c-c")
    @kb.add("c-q")
    def _(event): quit_action()

    style = Style([
        ("line", "#004444"),
    ])

    application = Application(
        layout=Layout(container, focused_element=input_field),
        key_bindings=kb,
        style=style,
        mouse_support=True,
        full_screen=False)

    set_log()
    application.run()