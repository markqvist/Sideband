from typing import Dict, Any, List

def merge_ordered_lists(md):
    """
    A plugin to merge consecutive "top-level" ordered lists into one,
    and also attach any intervening code blocks or blank lines to the
    last list item so that the final BBCode appears as a single list
    with multiple steps.

    This relies on a few assumptions:
      1) The only tokens between two ordered lists that should be merged
         are code blocks or blank lines (not normal paragraphs).
      2) We want any code block(s) right after a list item to appear in
         that same bullet item.
    """

    def rewrite_tokens(md, state):
        tokens = state.tokens
        merged = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # Check if this token is a top-level ordered list
            if (
                token["type"] == "list"
                and token.get("attrs", {}).get("ordered", False)
                and token.get("attrs", {}).get("depth", 0) == 0
            ):
                # Start new merged list
                current_depth = token["attrs"]["depth"]
                list_items = list(token["children"])  # bullet items in the first list
                i += 1

                # Continue until we run into something that's not:
                #   another top-level ordered list,
                #   or code blocks / blank lines (which we'll attach to the last bullet).
                while i < len(tokens):
                    nxt = tokens[i]

                    # If there's another ordered list at the same depth, merge its bullet items
                    if (
                        nxt["type"] == "list"
                        and nxt.get("attrs", {}).get("ordered", False)
                        and nxt.get("attrs", {}).get("depth", 0) == current_depth
                    ):
                        list_items.extend(nxt["children"])
                        i += 1

                    # If there's a code block or blank line, attach it to the *last* bullet item.
                    elif nxt["type"] in ["block_code", "blank_line"]:
                        if list_items:  # attach to last bullet item, if any
                            list_items[-1]["children"].append(nxt)
                        i += 1

                    else:
                        # Not a same-depth list or code block—stop merging
                        break

                # Create single merged list token
                merged.append(
                    {
                        "type": "list",
                        "children": list_items,
                        "attrs": {
                            "ordered": True,
                            "depth": current_depth,
                        },
                    }
                )

            else:
                # If not a top-level ordered list, just keep it as-is
                merged.append(token)
                i += 1

        # Replace the old tokens with the merged version
        state.tokens = merged

    # Attach to before_render_hooks so we can manipulate tokens before rendering
    md.before_render_hooks.append(rewrite_tokens)
    return md