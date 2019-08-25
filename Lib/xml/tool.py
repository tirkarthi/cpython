r"""Command-line tool to validate and pretty-print XML with XPath support.

Usage::

    $ echo '<html><body><p>hello</p></body></html>' | python -m xml.tool
    <html>
      <body>
        <p>hello</p>
      </body>
    </html>
    $ echo '<html><body><p>hello</p></body>' | python -m xml.tool
    no element found: line 2, column 0

    $ python -m xml.tool person.xml
    <root>
      <person name="Kate">
        <breakfast available="true">Idly</breakfast>
        <dinner available="true">Poori</dinner>
      </person>
      <person name="John">
        <breakfast available="false">Dosa</breakfast>
      </person>
    </root>

    $ python -m xml.tool --xpath './person/breakfast[.="Idly"]' person.xml
    <breakfast available="true">Idly</breakfast>

    $ python -m xml.tool --xpath './person/breakfast' person.xml
    <breakfast available="true">Idly</breakfast>
    <breakfast available="false">Dosa</breakfast>
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
            elem = ET.parse(infile)
            if xpath:
                for item in elem.iterfind(xpath):
                    outfile.write(ET.tostring(item, encoding='unicode'))
                    outfile.write('\n')
            else:
                root = next(elem.iter())
                ET.indent(root)
                outfile.write(ET.tostring(root, encoding='unicode'))
        except (ET.ParseError, SyntaxError) as e:
            raise SystemExit(e)


if __name__ == '__main__':
    main()
