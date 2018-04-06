import re

url_protocols = [
    'bitcoin:', 'ftp://', 'ftps://', 'geo:', 'git://', 'gopher://', 'http://',
    'https://', 'irc://', 'ircs://', 'magnet:', 'mailto:', 'mms://', 'news:',
    'nntp://', 'redis://', 'sftp://', 'sip:', 'sips:', 'sms:', 'ssh://',
    'svn://', 'tel:', 'telnet://', 'urn:', 'worldwind://', 'xmpp:', '//'
]

placeholder_tags = {'math': 'formula', 'code': 'codice'}
placeholder_tag_patterns = [(re.compile(
    r'<\s*%s(\s*| [^>]+?)>.*?<\s*/\s*%s\s*>' % (tag, tag),
    re.DOTALL | re.IGNORECASE), repl)
                            for tag, repl in placeholder_tags.items()]

image = re.compile(
    r"""^(http://|https://)([^][<>"\x00-\x20\x7F\s]+)    /([A-Za-z0-9_.,~%\-+&;#*?!=()@\x80-\xFF]+)\.((?i)gif|png|jpg|jpeg)$""",
    re.X | re.S | re.U)
link_url_class = r'[^][<>"\x00-\x20\x7F\s]'
anchor_class = r'[^][\x00-\x08\x0a-\x1F]'
link_brackets = re.compile(
    '\[(((?i)' + '|'.join(url_protocols) + ')' + link_url_class + r'+)' +
    r'\s*((?:' + anchor_class + r'|\[\[' + anchor_class + r'+\]\])' + r'*?)\]',
    re.S | re.U)

section = re.compile(r'(==+)\s*(.*?)\s*\1')
tail = re.compile(r'\w+')
bold_italic = re.compile(r"'''''(.*?)'''''")
bold = re.compile(r"'''(.*?)'''")
italic_quote = re.compile(r"''\"([^\"]*?)\"''")
italic = re.compile(r"''(.*?)''")
quote_quote = re.compile(r'""([^"]*?)""')
comment = re.compile(r'<!--.*?-->', re.DOTALL)
spaces = re.compile(r' {2,}')
dots = re.compile(r'\.{4,}')
tags = re.compile(r'(.*?)<(/?\w+)[^>]*>(?:([^<]*)(<.*?>)?)?')

syntaxhighlight = re.compile(
    '&lt;syntaxhighlight .*?&gt;(.*?)&lt;/syntaxhighlight&gt;', re.DOTALL)


class MagicWords(object):
    """
    One copy in each Extractor.

    @see https://doc.wikimedia.org/mediawiki-core/master/php/MagicWord_8php_source.html
    """
    names = [
        '!',
        'currentmonth',
        'currentmonth1',
        'currentmonthname',
        'currentmonthnamegen',
        'currentmonthabbrev',
        'currentday',
        'currentday2',
        'currentdayname',
        'currentyear',
        'currenttime',
        'currenthour',
        'localmonth',
        'localmonth1',
        'localmonthname',
        'localmonthnamegen',
        'localmonthabbrev',
        'localday',
        'localday2',
        'localdayname',
        'localyear',
        'localtime',
        'localhour',
        'numberofarticles',
        'numberoffiles',
        'numberofedits',
        'articlepath',
        'pageid',
        'sitename',
        'server',
        'servername',
        'scriptpath',
        'stylepath',
        'pagename',
        'pagenamee',
        'fullpagename',
        'fullpagenamee',
        'namespace',
        'namespacee',
        'namespacenumber',
        'currentweek',
        'currentdow',
        'localweek',
        'localdow',
        'revisionid',
        'revisionday',
        'revisionday2',
        'revisionmonth',
        'revisionmonth1',
        'revisionyear',
        'revisiontimestamp',
        'revisionuser',
        'revisionsize',
        'subpagename',
        'subpagenamee',
        'talkspace',
        'talkspacee',
        'subjectspace',
        'subjectspacee',
        'talkpagename',
        'talkpagenamee',
        'subjectpagename',
        'subjectpagenamee',
        'numberofusers',
        'numberofactiveusers',
        'numberofpages',
        'currentversion',
        'rootpagename',
        'rootpagenamee',
        'basepagename',
        'basepagenamee',
        'currenttimestamp',
        'localtimestamp',
        'directionmark',
        'contentlanguage',
        'numberofadmins',
        'cascadingsources',
    ]

    def __init__(self):
        self.values = {'!': '|'}

    def __getitem__(self, name):
        return self.values.get(name)

    def __setitem__(self, name, value):
        self.values[name] = value

    switches = ('__NOTOC__', '__FORCETOC__', '__TOC__', '__TOC__',
                '__NEWSECTIONLINK__', '__NONEWSECTIONLINK__', '__NOGALLERY__',
                '__HIDDENCAT__', '__NOCONTENTCONVERT__', '__NOCC__',
                '__NOTITLECONVERT__', '__NOTC__', '__START__', '__END__',
                '__INDEX__', '__NOINDEX__', '__STATICREDIRECT__',
                '__DISAMBIG__')


magicwords = re.compile('|'.join(MagicWords.switches))