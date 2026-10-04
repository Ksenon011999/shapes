import argparse
import sys


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Point({self.x}, {self.y})"


class Line:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return f"Line({self.start}, {self.end})"


class Circle:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def __str__(self):
        return f"Circle({self.center}, {self.radius})"


class PointShape:
    def __init__(self, p):
        self.p = p

    def __str__(self):
        return str(self.p)


class Parser:
    """Простой рекурсивный парсер без регулярок."""

    def __init__(self, text):
        self.text = text
        self.pos = 0

    def skip_ws(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def match_word(self, word):
        self.skip_ws()
        if self.text.startswith(word, self.pos):
            self.pos += len(word)
            return True
        return False

    def expect(self, ch):
        self.skip_ws()
        if self.pos < len(self.text) and self.text[self.pos] == ch:
            self.pos += 1
            return True
        return False

    def parse_number(self):
        self.skip_ws()
        start = self.pos
        if self.pos < len(self.text) and self.text[self.pos] in "+-":
            self.pos += 1
        has_digits = False
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            self.pos += 1
            has_digits = True
        if self.pos < len(self.text) and self.text[self.pos] == '.':
            self.pos += 1
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
                has_digits = True
        if not has_digits:
            raise ValueError("expected number")
        return float(self.text[start:self.pos])

    def parse_point(self):
        if not self.match_word("Point"):
            raise ValueError("expected Point")
        if not self.expect("("):
            raise ValueError("expected (")
        x = self.parse_number()
        if not self.expect(","):
            raise ValueError("expected ,")
        y = self.parse_number()
        if not self.expect(")"):
            raise ValueError("expected )")
        return Point(x, y)

    def parse(self):
        self.skip_ws()
        # пробуем Point, Line, Circle
        if self.text.startswith("Point", self.pos):
            p = self.parse_point()
            self.skip_ws()
            if self.pos != len(self.text):
                raise ValueError("trailing characters")
            return PointShape(p)

        if self.match_word("Line"):
            if not self.expect("("):
                raise ValueError("expected (")
            a = self.parse_point()
            if not self.expect(","):
                raise ValueError("expected ,")
            b = self.parse_point()
            if not self.expect(")"):
                raise ValueError("expected )")
            self.skip_ws()
            if self.pos != len(self.text):
                raise ValueError("trailing characters")
            return Line(a, b)

        if self.match_word("Circle"):
            if not self.expect("("):
                raise ValueError("expected (")
            c = self.parse_point()
            if not self.expect(","):
                raise ValueError("expected ,")
            r = self.parse_number()
            if not self.expect(")"):
                raise ValueError("expected )")
            self.skip_ws()
            if self.pos != len(self.text):
                raise ValueError("trailing characters")
            return Circle(c, r)

        raise ValueError("unknown shape")


def parse_shape(line):
    try:
        return Parser(line).parse()
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser(description="Shape file processor")
    ap.add_argument("-f", "--file", required=True, help="path to input file")
    ap.add_argument("-o", "--oper", required=True,
                    choices=["print", "count"], help="operation")
    args = ap.parse_args()

    shapes = []
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            for line_no, raw in enumerate(f, 1):
                line = raw.rstrip("\n").rstrip("\r")
                if not line.strip():
                    continue
                shape = parse_shape(line)
                if shape is None:
                    print(f"Skipping invalid line {line_no}: {line}",
                          file=sys.stderr)
                    continue
                shapes.append(shape)
    except OSError as e:
        print(f"Cannot open file: {e}", file=sys.stderr)
        sys.exit(1)

    if args.oper == "count":
        print(len(shapes))
    else:  # print
        for s in shapes:
            print(s)


if __name__ == "__main__":
    main()