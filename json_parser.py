"""A JSON validator. Setup: reads the file it's given; parsing comes in the next steps."""
import sys


def main(argv):
    if len(argv) != 2:
        print("usage: python3 json_parser.py FILE", file=sys.stderr)
        return 2
    open(argv[1], encoding="utf-8").read()
    print("not checked yet")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
