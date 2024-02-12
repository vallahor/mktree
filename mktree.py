from typing import Union
import argparse


class Directory:
    def __init__(self, name, indent_level, line):
        self.name = name
        self.directories = []
        self.files = []
        self.indent_level = indent_level
        self.created = False
        self.line = line


class File:
    def __init__(self, name, indent_level, line):
        self.name = name
        self.indent_level = indent_level
        self.line = line


class MkTree:
    input: str
    output: str
    tree_list: list[Union[Directory, File]]
    root: Directory
    indent: int
    text: str
    line: int

    def __init__(self, input, output, indent):
        self.input = input
        self.output = output
        self.tree_list = []
        self.root = Directory("root", 0, 1)
        self.indent = indent
        self.line = 0

    def run(self):
        self.gen_dir(self.input)

        self.text = self.gen_sh(self.root)

    def save_file(self):
        with open(self.output, "w") as f:
            f.write(self.text)


    def print_text(self):
        print(self.text)


    def parse_dir(self, dir: Directory, position: int = 0, indent_level: int = 0) -> int:
        index = 0

        while position + index < len(self.tree_list):
            node = self.tree_list[position + index]

            if node.indent_level < indent_level:
                break

            if isinstance(node, Directory):
                current_dir = node

                for directory in dir.directories:
                    if current_dir.name == directory.name:
                        raise Exception(f"The Directory {dir.name} at line {dir.line} has at least two directories with same name. Name: {directory.name}. First at line {directory.line} and second one at line {current_dir.line}")

                next_position = position + index + 1
                idx = self.parse_dir(current_dir, next_position, node.indent_level + 1)
                dir.directories.append(current_dir)
                index += idx
            elif isinstance(node, File):
                current_file = node
                for file in dir.files:
                    if current_file.name == file.name:
                        raise Exception(f"The Directory {dir.name} at line {dir.line} has at least two files with same name. Name: {file.name}. First at line {file.line} and second one at line {current_file.line}")

                dir.files.append(node)

            index += 1

        return index

    def make_dirs(self, dir_list: list[str], indent_level: int) -> (list[Directory], int):
        dirs = []
        for dir in dir_list:
            if dir == "":
                continue

            dir = Directory(f"{dir.lstrip()}/", indent_level, self.line)
            indent_level += 1
            dirs.append(dir)

        return dirs, indent_level

    def parse_line(self, text, indent_level):
        expand_section = None
        if "{" in text or "}" in text:
            temp = text[:-1].split("{", 1)

            if not text.endswith("}"):
                raise Exception(f"The Expansion Section at line {self.line} should end with }}")

            if len(temp) == 1:
                raise Exception(f"The Expansion Section at line {self.line} should start with {{")

            text = temp[0]
            expand_section = temp[1]

        dir_list = text.split("/")
        if len(dir_list) > 1:
            text = dir_list[-1]
            dir_list = dir_list[:-1]

            dirs, indent_level = self.make_dirs(dir_list, indent_level)
            self.tree_list.extend(dirs)

        if expand_section:
            expand_split = expand_section.replace(" ", "").split(",")

            items = []
            inner_text = ""
            for expand in expand_split:
                if "{" in expand:
                    inner_text += f"{expand}, "
                elif "}" in expand:
                    inner_text += expand
                    items.append(inner_text)
                    inner_text = ""
                else:
                    items.append(expand)

            for item in items:
                self.parse_line(item, indent_level)
            return

        if text == "":
            return

        file = File(text.lstrip(), indent_level, self.line)
        self.tree_list.append(file)

    def gen_dir(self, lines: list[str]) -> Directory:
        for line in lines:
            self.line += 1
            line = line.replace("\n", "").rstrip()
            line_cleaned = line.lstrip()

            if len(line_cleaned) == 0 or line_cleaned.startswith("--"):
                continue

            text = line_cleaned
            indent = len(line) - len(text)
            indent_level = indent / self.indent

            text = text.split("--")[0].rstrip()

            if indent % self.indent != 0:
                raise Exception(f"Wrong indentation at line {self.line} with value {indent}")

            self.parse_line(text, indent_level)

        _ = self.parse_dir(self.root)


    def make_line(self, cmd: str, path: str, fields: list[str]) -> str:
        sep, lhs, rhs = "", "", ""
        if len(fields) > 1:
            sep, lhs, rhs = ",", "{", "}"

        names = sep.join(fields)

        return f"{cmd} {path}{lhs}{names}{rhs}\n"


    def gen_sh(self, dir: Directory, path: str = "") -> str:
        mkdir = touch = txt = result = ""

        if len(dir.directories) == 1:
            dir.created = True
            directory = dir.directories[0]
            result = self.gen_sh(directory, f"{path}{directory.name}")
        else:
            dir_names = []
            if len(dir.directories) > 1:
                for directory in dir.directories:
                    directory.created = True
                    dir_names.append(directory.name[:-1])
                    result += self.gen_sh(directory, f"{path}{directory.name}")

            if not dir.created or len(dir_names) > 0:
                mkdir = self.make_line("mkdir -p", path, dir_names)

        if len(dir.files) > 0:
            files_name = [file.name for file in dir.files]
            touch = self.make_line("touch", path, files_name)

        txt += f"{mkdir}{result}{touch}"

        return txt


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", type=str, help="Input a inline tree struct")
parser.add_argument("-f", "--file", type=str, help="file containing directory tree")
parser.add_argument("-o", "--output", type=str, nargs="?", help="output filename", default="output.sh")
parser.add_argument("--indent", type=int, nargs="?", help="directory/file indent size", default=4)
parser.add_argument("--noprint", type=bool, action=argparse.BooleanOptionalAction, help="Don't print the script")
parser.add_argument("--save", type=bool, action=argparse.BooleanOptionalAction, help="Don't save any file", default=False)


def main():
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r") as f:
            lines = f.readlines()
        input = lines
    else:
        input = [args.input]

    mktree = MkTree(input, args.output, args.indent)
    mktree.run()

    if args.save:
        mktree.make_file()

    if not args.noprint:
        mktree.print_text()


if __name__ == "__main__":
    main()
