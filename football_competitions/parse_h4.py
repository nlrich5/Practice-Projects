from html.parser import HTMLParser
import sys


class HeaderParser(HTMLParser):
    def __init__(self, tag):
        super().__init__()
        self.tag = tag
        self.in_tag = False
        self.texts = []
        self.current_text = ""

    def handle_starttag(self, tag, attrs):
        if tag == self.tag:
            self.in_tag = True
            self.current_text = ""

    def handle_endtag(self, tag):
        if tag == self.tag:
            self.in_tag = False
            self.texts.append(self.current_text.strip())

    def handle_data(self, data):
        if self.in_tag:
            self.current_text += data


def parse_headers(filepath, tag):
    parser = HeaderParser(tag)
    with open(filepath, "r", encoding="utf-8") as f:
        parser.feed(f.read())
    return parser.texts


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_h4.py <html_file> [output_file] [--tag h3|h4]")
        sys.exit(1)

    # Parse --tag argument
    tag = "h4"
    args = []
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--tag" and i + 1 < len(sys.argv):
            tag = sys.argv[i + 1]
            i += 2
        else:
            args.append(sys.argv[i])
            i += 1

    if not args:
        print("Usage: python parse_h4.py <html_file> [output_file] [--tag h3|h4]")
        sys.exit(1)

    filepath = args[0]
    output_file = args[1] if len(args) > 1 else f"{tag}_headers.txt"

    headers = parse_headers(filepath, tag)

    with open(output_file, "w", encoding="utf-8") as f:
        for i, header in enumerate(headers, 1):
            f.write(f"{header}\n")

    print(f"Wrote {len(headers)} {tag} headers to {output_file}")
