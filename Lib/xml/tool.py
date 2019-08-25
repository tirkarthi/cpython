r"""Command-line tool to validate and pretty-print XML

Usage::

    $ echo '<html><body><p>hello</p></body></html>' | python -m xml.tool
    <html>
      <body>
        <p>hello</p>
      </body>
    </html>
    $ echo '<html><body><p>hello</p></body>' | python -m xml.tool
    no element found: line 2, column 0

"""
import argparse
import sys
from xml.etree import ElementTree as ET


def main():
    prog = 'python -m xml.tool'
    description = ('A simple command line interface for xml module '
                   'to validate and pretty-print XML objects.')
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument('--xpath', nargs='?', action='store',
                        help='XPath to be used on root node.')
    parser.add_argument('infile', nargs='?', type=argparse.FileType(),
                        help='an XML file to be validated or pretty-printed',
                        default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        help='write the output of infile to outfile',
                        default=sys.stdout)
    options = parser.parse_args()

    infile = options.infile
    outfile = options.outfile
    xpath = options.xpath

    with infile, outfile:
        try:
            elem = ET.XML(infile.read())
            if xpath:
                for item in elem.findall(xpath):
                    ET.indent(item)
                    outfile.write(ET.tostring(item).decode())
                    outfile.write('\n')
            else:
                ET.indent(elem)
                outfile.write(ET.tostring(elem).decode())
                outfile.write('\n')
        except (ET.ParseError, SyntaxError) as e:
            raise SystemExit(e)


if __name__ == '__main__':
    main()
