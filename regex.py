import re

url_protocols = [
    'bitcoin:', 'ftp://', 'ftps://', 'geo:', 'git://', 'gopher://', 'http://',
    'https://', 'irc://', 'ircs://', 'magnet:', 'mailto:', 'mms://', 'news:',
    'nntp://', 'redis://', 'sftp://', 'sip:', 'sips:', 'sms:', 'ssh://',
    'svn://', 'tel:', 'telnet://', 'urn:', 'worldwind://', 'xmpp:', '//'
]

image = re.compile(r"""^(http://|https://)([^][<>"\x00-\x20\x7F\s]+)
    /([A-Za-z0-9_.,~%\-+&;#*?!=()@\x80-\xFF]+)\.((?i)gif|png|jpg|jpeg)$""",
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