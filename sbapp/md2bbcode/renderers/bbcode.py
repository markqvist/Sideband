from mistune.core import BaseRenderer
from mistune.util import escape as escape_text, striptags, safe_entity
from urllib.parse import urljoin, urlparse


class BBCodeRenderer(BaseRenderer):
    """A renderer for converting Markdown to BBCode."""
    _escape: bool
    NAME = 'bbcode'

    def __init__(self, escape=False, domain=None):
        super(BBCodeRenderer, self).__init__()
        self._escape = escape
        self.domain = domain

    def render_token(self, token, state):
        func = self._get_method(token['type'])
        attrs = token.get('attrs')

        if 'raw' in token:
            text = token['raw']
        elif 'children' in token:
            text = self.render_tokens(token['children'], state)
        else:
            if attrs:
                return func(**attrs)
            else:
                return func()
        
        if attrs:
            return func(text, **attrs)
        else:
            return func(text)

    def safe_url(self, url: str) -> str:
        # Simple URL sanitization
        if url.startswith(('javascript:', 'vbscript:', 'data:')):
            return '#harmful-link'
        # Check if the URL is absolute by looking for a netloc part in the URL
        if not urlparse(url).netloc:
            url = urljoin(self.domain, url)
        return url

    def text(self, text: str) -> str:
        if self._escape:
            return escape_text(text)
        return text

    def emphasis(self, text: str) -> str:
        return '[i]' + text + '[/i]'

    def strong(self, text: str) -> str:
        return '[b]' + text + '[/b]'

    def link(self, text: str, url: str, title=None) -> str:
        return '[url=' + self.safe_url(url) + ']' + text + '[/url]'

    def image(self, text: str, url: str, title=None) -> str:
        alt_text = f' alt="{text}"' if text else ''
        img_tag = f'[img{alt_text}]' + self.safe_url(url) + '[/img]'
        # Check if alt text starts with 'pixel' and treat it as pixel art
        if text and text.lower().startswith('pixel'):
            return f'[pixelate]{img_tag}[/pixelate]'
        return img_tag

    def codespan(self, text: str) -> str:
        return '[icode]' + text + '[/icode]'

    def linebreak(self) -> str:
        return '\n'

    def softbreak(self) -> str:
        return '\n'

    def inline_html(self, html: str) -> str:
        if self._escape:
            return escape_text(html)
        return html

    def paragraph(self, text: str) -> str:
        return text + '\n\n'

    def heading(self, text: str, level: int, **attrs) -> str:
        if 1 <= level <= 3:
            return f"[HEADING={level}]{text}[/HEADING]\n"
        else:
            # Handle cases where level is outside 1-3
            return f"[HEADING=3]{text}[/HEADING]\n"
    
    def blank_line(self) -> str:
        return ''
    
    def thematic_break(self) -> str:
        return '[hr][/hr]\n'
    
    def block_text(self, text: str) -> str:
        return text
    
    def block_code(self, code: str, **attrs) -> str:
        # Renders blocks of code using the language specified in Markdown
        special_cases = {
            'plaintext': None  # Default [CODE]
        }

        if 'info' in attrs:
            lang_info = safe_entity(attrs['info'].strip())
            lang = lang_info.split(None, 1)[0].lower()
            # Check if the language needs special handling
            bbcode_lang = special_cases.get(lang, lang)  # Use the special case if it exists, otherwise use lang as is
            if bbcode_lang:
                return f"[CODE={bbcode_lang}]{escape_text(code)}[/CODE]\n"
            else:
                return f"[CODE]{escape_text(code)}[/CODE]\n"
        else:
            # No language specified, render with a generic [CODE] tag
            return f"[CODE]{escape_text(code)}[/CODE]\n"

    def block_quote(self, text: str) -> str:
        return '[QUOTE]\n' + text + '[/QUOTE]\n'

    def block_html(self, html: str) -> str:
        if self._escape:
            return '<p>' + escape_text(html.strip()) + '</p>\n'
        return html + '\n'

    def block_error(self, text: str) -> str:
        return '[color=red][icode]' + text + '[/icode][/color]\n'

    def list(self, text: str, ordered: bool, **attrs) -> str:
        depth = 0; sln = ""; tli = ""
        if "depth" in attrs: depth = attrs["depth"]
        if depth != 0: sln = "\n"
        if depth == 0: tli = "\n"
        def remove_empty_lines(text):
            lines = text.split('\n')
            non_empty_lines = [line for line in lines if line.strip() != '']
            nli = ""; dlm = "\n"+"  "*depth
            if depth != 0: nli = dlm
            return nli+dlm.join(non_empty_lines)

        text = remove_empty_lines(text)

        return sln+text+"\n"+tli
        # return '[{}]'.format(tag) + text + '[/list]\n'

    def list_item(self, text: str) -> str:
        return '• ' + text + '\n'
    
    def strikethrough(self, text: str) -> str:
        return '[s]' + text + '[/s]'
    
    def mark(self, text: str) -> str:
        # Simulate the mark effect with a background color in BBCode
        return '[mark]' + text + '[/mark]'

    def insert(self, text: str) -> str:
        # Use underline to represent insertion
        return '[u]' + text + '[/u]'

    def superscript(self, text: str) -> str:
        return '[sup]' + text + '[/sup]'

    def subscript(self, text: str) -> str:
        return '[sub]' + text + '[/sub]'
    
    def inline_spoiler(self, text: str) -> str:
        return '[ISPOILER]' + text + '[/ISPOILER]'

    def block_spoiler(self, text: str) -> str:
        return '[SPOILER]\n' + text + '\n[/SPOILER]'

    def footnote_ref(self, key: str, index: int):
        # Use superscript for the footnote reference
        return f'[sup][u][JUMPTO=fn-{index}]{index}[/JUMPTO][/u][/sup]'

    def footnotes(self, text: str):
        # Optionally wrap all footnotes in a specific section if needed
        return '[b]Footnotes:[/b]\n' + text

    def footnote_item(self, text: str, key: str, index: int):
        # Define the footnote with an anchor at the end of the document
        return f'[ANAME=fn-{index}]{index}[/ANAME]. {text}'
    
    def table(self, children, **attrs):
        # Starting with a full-width table by default if not specified
        # width = attrs.get('width', '100%') # comment out until XF 2.3
        # return f'[TABLE width="{width}"]\n' + children + '[/TABLE]\n' # comment out until XF 2.3
        return '[TABLE]\n' + children + '[/TABLE]\n'

    def table_head(self, children, **attrs):
        return '[TR]\n' + children + '[/TR]\n'

    def table_body(self, children, **attrs):
        return children

    def table_row(self, children, **attrs):
        return '[TR]\n' + children + '[/TR]\n'

    def table_cell(self, text, align=None, head=False, **attrs):
        # BBCode does not support direct cell alignment,
        # use [LEFT], [CENTER], or [RIGHT] tags

        # Use th for header cells and td for normal cells
        tag = 'TH' if head else 'TD'

        # Initialize alignment tags
        alignment_start = ''
        alignment_end = ''

        if align == 'center':
            alignment_start = '[CENTER]'
            alignment_end = '[/CENTER]'
        elif align == 'right':
            alignment_start = '[RIGHT]'
            alignment_end = '[/RIGHT]'
        elif align == 'left':
            alignment_start = '[LEFT]'
            alignment_end = '[/LEFT]'

        return f'[{tag}]{alignment_start}{text}{alignment_end}[/{tag}]\n'

    def task_list_item(self, text: str, checked: bool = False) -> str:
        # Using emojis to represent the checkbox
        checkbox_emoji = '󰱒' if checked else '󰄱'
        return checkbox_emoji + ' ' + text + '\n'

    def def_list(self, text: str) -> str:
        # No specific BBCode tag for <dl>, so we just use the plain text grouping
        return '\n' + text + '\n'

    def def_list_head(self, text: str) -> str:
        return '[b]' + text + '[/b]' + ' ' + ':' + '\n'

    def def_list_item(self, text: str) -> str:
        return '[INDENT]' + text + '[/INDENT]\n'
    
    def abbr(self, text: str, title: str) -> str:
        if title:
            return f'[abbr={title}]{text}[/abbr]'
        return text