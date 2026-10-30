"""A JSON validator. Step 1: a tiny lexer and parser that accept only an empty object."""
import sys


def tokens(text):
    for ch in text:
        if ch in " \t\r\n":
            continue
        if ch in "{}":
            yield ch
        else:
            raise ValueError(f"unexpected character {ch!r}")


def parse(text):
    toks = list(tokens(text))
    if toks != ["{", "}"]:
        raise ValueError("expected an empty object")


def main(argv):
    if len(argv) != 2:
        print("usage: python3 json_parser.py FILE", file=sys.stderr)
        return 2
    try:
        parse(open(argv[1], encoding="utf-8").read())
    except ValueError as e:
        print(f"invalid: {e}")
        return 1
    print("valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
