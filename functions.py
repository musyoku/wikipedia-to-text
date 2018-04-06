import re
from itertools import zip_longest
from html.entities import name2codepoint
import regex
import collection

self_closing_tags = [
    re.compile(r"<\s*%s\b[^>]*/\s*>" % tag, re.DOTALL | re.IGNORECASE)
    for tag in collection.tags_self_closing
]


def makeInternalLink(title, label):
    colon = title.find(":")
    if colon > 0 and title[:colon] not in collection.acceptedNamespaces:
        return ""
    if colon == 0:
        # drop also :File:
        colon2 = title.find(":", colon + 1)
        if colon2 > 1 and title[colon + 1:
                                colon2] not in collection.acceptedNamespaces:
            return ""
    return label


def findBalanced(text, openDelim=["[["], closeDelim=["]]"]):
    openPat = "|".join([re.escape(x) for x in openDelim])
    # pattern for delimiters expected after each opening delimiter
    afterPat = {
        o: re.compile(openPat + "|" + c, re.DOTALL)
        for o, c in zip(openDelim, closeDelim)
    }
    stack = []
    start = 0
    cur = 0
    # end = len(text)
    startSet = False
    startPat = re.compile(openPat)
    nextPat = startPat
    while True:
        next = nextPat.search(text, cur)
        if not next:
            return
        if not startSet:
            start = next.start()
            startSet = True
        delim = next.group(0)
        if delim in openDelim:
            stack.append(delim)
            nextPat = afterPat[delim]
        else:
            stack.pop()
            # assert opening == openDelim[closeDelim.index(next.group(0))]
            if stack:
                nextPat = afterPat[stack[-1]]
            else:
                yield start, next.end()
                nextPat = startPat
                start = next.end()
                startSet = False
        cur = next.end()


def replace_internal_links(text):
    cur = 0
    res = ""
    for s, e in findBalanced(text):
        m = regex.tail.match(text, e)
        if m:
            trail = m.group(0)
            end = m.end()
        else:
            trail = ""
            end = e
        inner = text[s + 2:e - 2]
        # find first |
        pipe = inner.find("|")
        if pipe < 0:
            title = inner
            label = title
        else:
            title = inner[:pipe].rstrip()
            # find last |
            curp = pipe + 1
            for s1, e1 in findBalanced(inner):
                last = inner.rfind("|", curp, s1)
                if last >= 0:
                    pipe = last  # advance
                curp = e1
            label = inner[pipe + 1:].strip()
        res += text[cur:s] + makeInternalLink(title, label) + trail
        cur = end
    return res + text[cur:]


def extract_pages_from_archive(input):
    page = []
    id = None
    ns = "0"
    last_id = None
    inText = False
    redirect = False
    for line in input:
        line = line.decode("utf-8")
        if "<" not in line:  # faster than doing re.search()
            if inText:
                page.append(line)
            continue
        m = regex.tags.search(line)
        if not m:
            continue
        tag = m.group(2)
        if tag == "page":
            page = []
            redirect = False
        elif tag == "id" and not id:  # skip nested <id>
            id = m.group(3)
        elif tag == "title":
            title = m.group(3)
        elif tag == "ns":
            ns = m.group(3)
        elif tag == "redirect":
            redirect = True
        elif tag == "text":
            inText = True
            line = line[m.start(3):m.end(3)]
            page.append(line)
            if m.lastindex == 4:  # open-close
                inText = False
        elif tag == "/text":
            if m.group(1):
                page.append(m.group(1))
            inText = False
        elif inText:
            page.append(line)
        elif tag == "/page":
            if id != last_id and not redirect:
                yield (id, title, ns, page)
                last_id = id
                ns = "0"
            id = None
            page = []


def replace_external_links(text):
    s = ""
    cur = 0
    for m in regex.link_brackets.finditer(text):
        s += text[cur:m.start()]
        cur = m.end()
        label = m.group(3)
        m = regex.image.match(label)
        s += label
    return s + text[cur:]


def drop_nested_tags(text, openDelim, closeDelim):
    regex_open = re.compile(openDelim, re.IGNORECASE)
    regex_close = re.compile(closeDelim, re.IGNORECASE)
    spans = []
    nest = 0
    start = regex_open.search(text, 0)
    if not start:
        return text
    end = regex_close.search(text, start.end())
    next = start
    while end:
        next = regex_open.search(text, next.end())
        if not next:
            while nest:
                nest -= 1
                end0 = regex_close.search(text, end.end())
                if end0:
                    end = end0
                else:
                    break
            spans.append((start.start(), end.end()))
            break
        while end.end() < next.start():
            if nest:
                nest -= 1
                last = end.end()
                end = regex_close.search(text, end.end())
                if not end:
                    if spans:
                        span = (spans[0][0], last)
                    else:
                        span = (start.start(), last)
                    spans = [span]
                    break
            else:
                spans.append((start.start(), end.end()))
                start = next
                end = regex_close.search(text, next.end())
                break  # { }
        if next != start:
            # { { }
            nest += 1
    return drop_span_tags(spans, text)


def drop_span_tags(spans, text):
    spans.sort()
    res = ""
    offset = 0
    for s, e in spans:
        if offset <= s:  # handle nesting
            if offset < s:
                res += text[offset:s]
            offset = e
    res += text[offset:]
    return res


def compact(text):
    page = []
    headers = {}
    emptySection = False
    listLevel = []

    for line in text.split("\n"):
        if not line:
            continue
        m = regex.section.match(line)
        if m:
            continue
        elif line.startswith("++"):
            title = line[2:-2]
            if title:
                if title[-1] not in "!?":
                    title += "."
                page.append(title)
        elif line[0] == ":":
            continue
        elif line[0] in "*#;:":
            i = 0
            for c, n in zip_longest(listLevel, line, fillvalue=""):
                if not n or n not in "*#;:":
                    if c:
                        listLevel = listLevel[:-1]
                        continue
                    else:
                        break
                if c != n and (not c or (c not in ";:" and n not in ";:")):
                    if c:
                        listLevel = listLevel[:-1]
                    listLevel += n
                i += 1
            n = line[i - 1]
            line = line[i:].strip()
        elif len(listLevel):
            page.append(line)
            listLevel = []

        elif line[0] in "{|" or line[-1] == "}":
            continue
        elif (line[0] == "(" and line[-1] == ")") or line.strip(".-") == "":
            continue
        elif len(headers):
            headers.clear()
            page.append(line)
            emptySection = False
        elif not emptySection:
            if line[0] != " ":
                page.append(line)
    return page


def unescape(text):
    def fixup(m):
        text = m.group(0)
        code = m.group(1)
        try:
            if text[1] == "#":  # character reference
                if text[2] == "x":
                    return chr(int(code[1:], 16))
                else:
                    return chr(int(code))
            else:  # named entity
                return chr(name2codepoint[code])
        except:
            return text  # leave as is

    return re.sub("&#?(\w+);", fixup, text)


def clean(text):
    text = drop_nested_tags(text, r"{{", r"}}")
    text = drop_nested_tags(text, r"{\|", r"\|}")
    text = replace_external_links(text)
    text = replace_internal_links(text)
    text = regex.magicwords.sub("", text)
    res = ""
    cur = 0
    for m in regex.syntaxhighlight.finditer(text):
        res += unescape(text[cur:m.start()]) + m.group(1)
        cur = m.end()
    text = res + unescape(text[cur:])
    text = regex.bold_italic.sub(r"\1", text)
    text = regex.bold.sub(r"\1", text)
    text = regex.italic_quote.sub(r'"\1"', text)
    text = regex.italic.sub(r'"\1"', text)
    text = regex.quote_quote.sub(r'"\1"', text)
    text = text.replace("'''", '').replace("''", '"')

    spans = []
    for m in regex.comment.finditer(text):
        spans.append((m.start(), m.end()))
    for pattern in self_closing_tags:
        for m in pattern.finditer(text):
            spans.append((m.start(), m.end()))
    for left, right in collection.ignored_tag_patterns:
        for m in left.finditer(text):
            spans.append((m.start(), m.end()))
        for m in right.finditer(text):
            spans.append((m.start(), m.end()))

    text = drop_span_tags(spans, text)
    for tag in collection.discard_elements:
        text = drop_nested_tags(text, r"<\s*%s\b[^>/]*>" % tag, r"<\s*/\s*%s>" % tag)

    text = unescape(text)
    for pattern, placeholder in regex.placeholder_tag_patterns:
        index = 1
        for match in pattern.finditer(text):
            text = text.replace(match.group(), '%s_%d' % (placeholder, index))
            index += 1

    text = text.replace("<<", u"Â«").replace(">>", u"Â»")

    text = text.replace("\t", " ")
    text = regex.spaces.sub(" ", text)
    text = regex.dots.sub("...", text)
    text = re.sub(u" (,:\.\)\]Â»)", r"\1", text)
    text = re.sub(u"(\[\(Â«) ", r"\1", text)
    text = re.sub(r"（）", "", text)
    text = re.sub(r"\n\W+?\n", "\n", text, flags=re.U)
    text = text.replace(",,", ",").replace(",.", ".")
    return text