# this is for debugging the custom mistune renderer bbcode.py
import argparse
import mistune
import json  # Import the json module for serialization
from mistune.plugins.formatting import strikethrough, mark, superscript, subscript, insert
from mistune.plugins.table import table, table_in_list
from mistune.plugins.footnotes import footnotes
from mistune.plugins.task_lists import task_lists
from mistune.plugins.def_list import def_list
from mistune.plugins.abbr import abbr
from mistune.plugins.spoiler import spoiler

#local
from sbapp.md2bbcode.plugins.merge_lists import merge_ordered_lists

def convert_markdown_to_ast(input_filepath, output_filepath):
    # Initialize Markdown parser with no renderer to produce an AST
    markdown_parser = mistune.create_markdown(renderer=None, plugins=[strikethrough, mark, superscript, subscript, insert, table, footnotes, task_lists, def_list, abbr, spoiler, table_in_list, merge_ordered_lists])
    
    # Read the input Markdown file
    with open(input_filepath, 'r', encoding='utf-8') as md_file:
        markdown_text = md_file.read()
    
    # Convert Markdown text to AST
    ast_text = markdown_parser(markdown_text)
    
    # Serialize the AST to a JSON string
    ast_json = json.dumps(ast_text, indent=4)
    
    # Write the output AST to a new file in JSON format
    with open(output_filepath, 'w', encoding='utf-8') as ast_file:
        ast_file.write(ast_json)

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='Convert Markdown file to AST file (JSON format).')
    # Add arguments
    parser.add_argument('input', help='Input Markdown file path')
    parser.add_argument('output', help='Output AST file path (JSON format)')
    # Parse arguments
    args = parser.parse_args()
    
    # Convert the Markdown to AST using the provided paths
    convert_markdown_to_ast(args.input, args.output)

if __name__ == '__main__':
    main()
