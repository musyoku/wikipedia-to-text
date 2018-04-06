import re
import argparse
import fileinput
import urllib

import regex
import collection
import functions

knownNamespaces = set(['Template'])
templateKeys = set(['10', '828'])

urlbase = ""


def get_url(uid):
    return "%s?curid=%s" % (urlbase, uid)


def main():
    global urlbase
    f = fileinput.FileInput(args.input, openhook=fileinput.hook_compressed)
    for line in f:
        line = line.decode("utf-8")
        m = regex.tags.search(line)
        if not m:
            continue
        tag = m.group(2)
        if tag == 'base':
            base = m.group(3)
            urlbase = base[:base.rfind("/")]
        elif tag == 'namespace':
            # knownNamespaces.add(m.group(3))
            if re.search('key="10"', line):
                templateNamespace = m.group(3)
                templatePrefix = templateNamespace + ':'
            elif re.search('key="828"', line):
                moduleNamespace = m.group(3)
                modulePrefix = moduleNamespace + ':'
        elif tag == '/siteinfo':
            break

    for (id, title, ns, page) in functions.pages_from(f):
        if ns not in templateKeys:
            url = get_url(id)
            text = ''.join(page)
            text = functions.clean(text)
            paragraphs = []
            for line in functions.compact(text):
                paragraphs.append(line)
            print(title)
            print("".join(paragraphs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # 以下のどちらかを必ず指定
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="jawiki-latest-pages-articles.xml.bz2のパスを指定")
    args = parser.parse_args()
    main()