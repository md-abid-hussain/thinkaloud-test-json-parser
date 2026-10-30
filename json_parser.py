"""A JSON validator: exits 0 when the file is valid JSON (RFC 8259) and 1 when it isn't, saying where and why.

A recursive-descent parser over the characters: each grammar rule (value, object, array, string, number) is a method.
"""
import sys

MAX_DEPTH = 256
DIGITS = "0123456789"


class JSONError(Exception):
    def __init__(self, message, pos, text):
        line = text.count("\n", 0, pos) + 1
        column = pos - (text.rfind("\n", 0, pos) + 1) + 1
        super().__init__(f"{message} at line {line}, column {column}")


class Parser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.depth = 0

    def error(self, message, pos=None):
        raise JSONError(message, self.pos if pos is None else pos, self.text)

    def peek(self):
        return self.text[self.pos] if self.pos < len(self.text) else ""

    def at(self, chars):
        ch = self.peek()
        return ch != "" and ch in chars

    def found(self):
        return repr(self.peek()) if self.peek() else "the end of the input"

    def skip_ws(self):
        while self.at(" \t\n\r"):
            self.pos += 1

    def expect(self, ch):
        if self.peek() != ch:
            self.error(f"expected {ch!r}, found {self.found()}")
        self.pos += 1

    def parse(self):
        self.skip_ws()
        if not self.peek():
            self.error("empty input")
        self.value()
        self.skip_ws()
        if self.pos != len(self.text):
            self.error(f"unexpected {self.found()} after the value")

    def value(self):
        ch = self.peek()
        if ch == "{":
            self.nested("{", "}", self.member)
        elif ch == "[":
            self.nested("[", "]", self.value)
        elif ch == '"':
            self.string()
        elif ch == "-" or self.at(DIGITS):
            self.number()
        else:
            for word in ("true", "false", "null"):
                if self.text.startswith(word, self.pos):
                    self.pos += len(word)
                    return
            self.error(f"unexpected {self.found()}")

    def nested(self, open_ch, close_ch, item):
        self.depth += 1
        if self.depth > MAX_DEPTH:
            self.error(f"nested deeper than {MAX_DEPTH} levels")
        self.expect(open_ch)
        self.skip_ws()
        if self.peek() == close_ch:
            self.pos += 1
            self.depth -= 1
            return
        while True:
            item()
            self.skip_ws()
            if self.peek() == ",":
                self.pos += 1
                self.skip_ws()
            elif self.peek() == close_ch:
                self.pos += 1
                self.depth -= 1
                return
            else:
                self.error(f"expected ',' or {close_ch!r}, found {self.found()}")

    def member(self):
        if self.peek() != '"':
            self.error(f"expected a string key, found {self.found()}")
        self.string()
        self.skip_ws()
        self.expect(":")
        self.skip_ws()
        self.value()

    def string(self):
        start = self.pos
        self.expect('"')
        while True:
            if self.pos >= len(self.text):
                self.error("string never closed", start)
            ch = self.text[self.pos]
            if ch == '"':
                self.pos += 1
                return
            if ch == "\\":
                self.pos += 1
                if self.at('"\\/bfnrt'):
                    self.pos += 1
                elif self.peek() == "u":
                    hexes = self.text[self.pos + 1:self.pos + 5]
                    if len(hexes) != 4 or any(c not in "0123456789abcdefABCDEF" for c in hexes):
                        self.error("\\u must be followed by 4 hex digits")
                    self.pos += 5
                else:
                    self.error(f"invalid escape \\{self.peek()}")
            elif ord(ch) < 0x20:
                self.error("control character in a string must be escaped")
            else:
                self.pos += 1

    def digits(self):
        if not self.at(DIGITS):
            self.error(f"expected a digit, found {self.found()}")
        while self.at(DIGITS):
            self.pos += 1

    def number(self):
        if self.peek() == "-":
            self.pos += 1
        if self.peek() == "0":
            self.pos += 1  # a leading zero stands alone: 0123 is not a number
        else:
            self.digits()
        if self.peek() == ".":
            self.pos += 1
            self.digits()
        if self.at("eE"):
            self.pos += 1
            if self.at("+-"):
                self.pos += 1
            self.digits()


def main(argv):
    if len(argv) != 2:
        print("usage: python3 json_parser.py FILE", file=sys.stderr)
        return 2
    sys.setrecursionlimit(5000)
    try:
        text = open(argv[1], "rb").read().decode("utf-8")
    except UnicodeDecodeError:
        print("invalid: the file is not UTF-8")
        return 1
    try:
        Parser(text).parse()
    except JSONError as e:
        print(f"invalid: {e}")
        return 1
    print("valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
