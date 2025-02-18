import mistune
from mistune.core import BaseRenderer
from mistune.plugins.formatting import strikethrough, mark, superscript, subscript, insert
from mistune.plugins.table import table, table_in_list
from mistune.plugins.footnotes import footnotes
from mistune.plugins.task_lists import task_lists
from mistune.plugins.spoiler import spoiler
from mistune.util import escape as escape_text, safe_entity

def mdconv(markdown_text, domain=None, debug=False):
    parser = mistune.create_markdown(renderer=BBRenderer(), plugins=[strikethrough, mark, superscript, subscript, insert, footnotes, task_lists, spoiler])
    return parser(markdown_text)

class BBRenderer(BaseRenderer):
    NAME = "bbcode"

    def __init__(self, escape=False):
        super(BBRenderer, self).__init__()
        self._escape = escape

    def render_token(self, token, state):
        func = self._get_method(token["type"])
        attrs = token.get("attrs")

        if "raw" in token: text = token["raw"]
        elif "children" in token: text = self.render_tokens(token["children"], state)
        else:
            if attrs: return func(**attrs)
            else: return func()
        
        if attrs: return func(text, **attrs)
        else: return func(text)

    # Simple renderers
    def emphasis(self, text): return f"[i]{text}[/i]"
    def strong(self, text): return f"[b]{text}[/b]"
    def codespan(self, text): return f"[icode]{text}[/icode]"
    def linebreak(self): return "\n"
    def softbreak(self): return "\n"
    def list_item(self, text): return f"• {text}\n"
    def task_list_item(self, text, checked=False): e = "󰱒" if checked else "󰄱"; return f"{e} {text}\n"
    def strikethrough(self, text): return f"[s]{text}[/s]"
    def insert(self, text): return f"[u]{text}[/u]"
    def inline_spoiler(self, text): return f"[ISPOILER]{text}[/ISPOILER]"
    def block_spoiler(self, text): return f"[SPOILER]\n{text}\n[/SPOILER]"
    def block_error(self, text): return f"[color=red][icode]{text}[/icode][/color]\n"
    def block_html(self, html): return ""
    def link(self, text, url, title=None): return f"[u]{text}[/u] ({url})"
    def footnote_ref(self, key, index): return f"[sup][u]{index}[/u][/sup]"
    def footnotes(self, text): return f"[b]Footnotes[/b]\n{text}"
    def footnote_item(self, text, key, index): return f"[ANAME=footnote-{index}]{index}[/ANAME]. {text}"
    def superscript(self, text: str) -> str: return f"[sup]{text}[/sup]"
    def subscript(self, text): return f"[sub]{text}[/sub]"
    def block_quote(self, text: str) -> str: return f"| [i]{text}[/i]"
    def paragraph(self, text): return f"{text}\n\n"
    def blank_line(self): return ""    
    def block_text(self, text): return text

    # Renderers needing some logic
    def text(self, text):
        if self._escape: return escape_text(text)
        else: return text

    def inline_html(self, html: str) -> str:
        if self._escape: return escape_text(html)
        else: return html

    def heading(self, text, level, **attrs):
        if 1 <= level <= 3: return f"[HEADING={level}]{text}[/HEADING]\n"
        else: return f"[HEADING=3]{text}[/HEADING]\n"
    
    def block_code(self, code: str, **attrs) -> str:
        special_cases = {"plaintext": None, "text": None, "txt": None}
        if "info" in attrs:
            lang_info = safe_entity(attrs["info"].strip())
            lang = lang_info.split(None, 1)[0].lower()
            bbcode_lang = special_cases.get(lang, lang)
            if bbcode_lang: return f"[CODE={bbcode_lang}]{escape_text(code)}[/CODE]\n"
            else: return f"[CODE]{escape_text(code)}[/CODE]\n"
        
        else: return f"[CODE]{escape_text(code)}[/CODE]\n"

    def list(self, text, ordered, **attrs):
        depth = 0; sln = ""; tli = ""
        if "depth" in attrs: depth = attrs["depth"]
        if depth != 0: sln = "\n"
        if depth == 0: tli = "\n"
        def remove_empty_lines(text):
            lines = text.split("\n")
            non_empty_lines = [line for line in lines if line.strip() != ""]
            nli = ""; dlm = "\n"+"  "*depth
            if depth != 0: nli = dlm
            return nli+dlm.join(non_empty_lines)

        text = remove_empty_lines(text)
        return sln+text+"\n"+tli

    # TODO: Implement various table types and other special formatting
    def table(self, children, **attrs): return children
    def table_head(self, children, **attrs): return children
    def table_body(self, children, **attrs): return children
    def table_row(self, children, **attrs): return children
    def table_cell(self, text, align=None, head=False, **attrs): return f"{text}\n"
    def def_list(self, text): return f"{text}\n"
    def def_list_head(self, text): return f"{text}\n"
    def def_list_item(self, text): return f"{text}\n"
    def abbr(self, text, title): return text
    def mark(self, text): return text
    def image(self, text, url, title=None): return ""
    def thematic_break(self): return "-------------\n"