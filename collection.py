import re

tags_self_closing = ("br", "hr", "nobr", "ref", "references", "nowiki")
tags_ignored = ("abbr", "b", "big", "blockquote", "center", "cite", "em",
                "font", "h1", "h2", "h3", "h4", "hiero", "i", "kbd", "nowiki",
                "p", "plaintext", "s", "span", "strike", "strong", "tt", "u",
                "var")

discard_elements = [
    "gallery", "timeline", "noinclude", "pre", "table", "tr", "td", "th",
    "caption", "div", "form", "input", "select", "option", "textarea", "ul",
    "li", "ol", "dl", "dt", "dd", "menu", "dir", "ref", "references", "img",
    "imagemap", "source", "small", "sub", "sup"
]
acceptedNamespaces = ["w", "wiktionary", "wikt"]
ignored_tag_patterns = []

for tag in tags_ignored:
    left = re.compile(r"<%s\b.*?>" % tag, re.IGNORECASE | re.DOTALL)
    right = re.compile(r"</\s*%s>" % tag, re.IGNORECASE)
    ignored_tag_patterns.append((left, right))