# uses a custom mistune renderer to convert Markdown to BBCode. The custom renderer is defined in the bbcode.py file.
# pass --debug to save the output to readme.1stpass (main.py) and readme.finalpass (html2bbcode)
# for further debugging, you can convert the markdown file to AST using md2ast.py. Remember to load the plugin(s) you want to test.

#standard library
import argparse
import sys
import RNS

# mistune
import mistune
from mistune.plugins.formatting import strikethrough, mark, superscript, subscript, insert
from mistune.plugins.table import table, table_in_list
from mistune.plugins.footnotes import footnotes
from mistune.plugins.task_lists import task_lists
from mistune.plugins.def_list import def_list
from mistune.plugins.abbr import abbr
from mistune.plugins.spoiler import spoiler

if RNS.vendor.platformutils.is_android():
    from .plugins.merge_lists import merge_ordered_lists
    from .renderers.bbcode import BBCodeRenderer
    from .html2bbcode import process_html
else:
    from sbapp.md2bbcode.plugins.merge_lists import merge_ordered_lists
    from sbapp.md2bbcode.renderers.bbcode import BBCodeRenderer
    from sbapp.md2bbcode.html2bbcode import process_html

def convert_markdown_to_bbcode(markdown_text, domain):
    # Create a Markdown parser instance using the custom BBCode renderer
    markdown_parser = mistune.create_markdown(renderer=BBCodeRenderer(domain=domain), plugins=[strikethrough, mark, superscript, subscript, insert, table, footnotes, task_lists, def_list, abbr, spoiler, table_in_list, merge_ordered_lists])

    # Convert Markdown text to BBCode
    return markdown_parser(markdown_text)

def process_readme(markdown_text, domain=None, debug=False):
    # Convert Markdown to BBCode
    bbcode_text = convert_markdown_to_bbcode(markdown_text, domain)

    # Convert BBCode formatted as HTML to final BBCode
    final_bbcode = process_html(bbcode_text, debug, 'readme.finalpass')

    return final_bbcode

def main():
    parser = argparse.ArgumentParser(description='Convert Markdown file to BBCode with HTML processing.')
    parser.add_argument('input', help='Input Markdown file path')
    parser.add_argument('--domain', help='Domain to prepend to relative URLs')
    parser.add_argument('--debug', action='store_true', help='Output intermediate results to files for debugging')
    args = parser.parse_args()

    if args.input == '-':
        # Read Markdown content from stdin
        markdown_text = sys.stdin.read()
    else:
        with open(args.input, 'r', encoding='utf-8') as md_file:
            markdown_text = md_file.read()

    # Process the readme and get the final BBCode
    final_bbcode = process_readme(markdown_text, args.domain, args.debug)

    # Optionally, print final BBCode to console
    if not args.debug:
        print(final_bbcode)

if __name__ == '__main__':
    main()
