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
    filename: str
    output: str
    tree_list: list[Union[Directory, File]]
    root: Directory
    indent: int
    text: str
    line: int

    def __init__(self, filename, output, indent):
        self.filename = filename
        self.output = output
        self.tree_list = []
        self.root = Directory("root", 0, 1)
        self.indent = indent
        self.line = 0

    def make_file(self):
        with open(self.filename, "r") as f:
            lines = f.readlines()
        self.gen_dir(lines)

        self.text = self.gen_sh(self.root)

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


    def gen_dir(self, lines: list[str]) -> Directory:
        for line in lines:
            self.line += 1
            line = line.replace("\n", "").rstrip()

            if len(line.lstrip()) == 0:
                continue

            name = line.lstrip()
            indent = len(line) - len(name)
            indent_level = indent / self.indent

            if indent % self.indent != 0:
                raise Exception(f"Wrong indentation at line {self.line} with value {indent}")

            dir_list = name.split("/")
            if len(dir_list) > 1:
                name = dir_list[-1]


                dir_list = dir_list[:-1]
                dirs, indent_level = self.make_dirs(dir_list, indent_level)
                self.tree_list.extend(dirs)

            if "--" in name:
                name = name.lstrip().split("--")[0]

            if name == "":
                continue

            file = File(name.lstrip(), indent_level, self.line)
            self.tree_list.append(file)

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

        txt += f"{mkdir}{touch}{result}"

        return txt


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", type=str, help="file containing directory tree", required=True)
parser.add_argument("-o", "--output", type=str, help="output filename", required=True)
parser.add_argument("--indent", type=int, nargs="?", help="directory/file indent size", default=4)
parser.add_argument("--print", type=bool, action=argparse.BooleanOptionalAction, help="print file content")


def main():
    args = parser.parse_args()

    mktree = MkTree(args.input, args.output, args.indent)
    mktree.make_file()

    if args.print:
        mktree.print_text()


if __name__ == "__main__":
    main()
