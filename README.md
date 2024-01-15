# MkTree

Generate a tree file structure script from a txt file.

`input.txt`
```
css/
    styles.css
    version/
index.html

-- This is a comment!
javascript/
    index.js
    timer.js -- Timer
    modules/ -- Modules directory
        lib1/index.js
        lib2/ src/ index.js -- spaces can be inserted between dirs and files
        lib3/src/index.js
            modules/ -- lib3 modules is empty
    stuff.js

README.md
```

`output.sh`
```
mkdir -p {css,javascript}
mkdir -p css/version/
touch css/styles.css
mkdir -p javascript/modules/{lib1,lib2,lib3}
touch javascript/modules/lib1/index.js
mkdir -p javascript/modules/lib2/src/
touch javascript/modules/lib2/src/index.js
mkdir -p javascript/modules/lib3/{src,modules}
touch javascript/modules/lib3/src/index.js
touch javascript/{index.js,timer.js ,stuff.js}
touch {index.html,README.md}
```

# Explaining the syntax

- Indentation will determine where directories and files will be placed.
- Every directory should end with an `/`.
- Comments starts with `--` and should be make in a empty line or in the end of line.

## usage
```sh
python mktree.py -i input.txt --nosave
python mktree.py -i input.txt -o output.sh --indent 4
```

## Commands

- `-i`, `--input`: input txt filename
- `-o`, `--output`: output script filename. Default: `output.sh`
- `--indent`: indent size of directories and files. That's not strict, it's possible to multiples of the indent value.
- `--nosave`: Don't save
- `--noprint`: Don't print

# Errors

If the directory have at least two directories or files with the same name an error will be thrown saying the diretory name and it's position in the txt file.

```
ex/
    a1/b/file_b.txt
    a2/b/file_b.txt
    a3/b/file_b.txt
    a1/b/file_b.txt
```
`Exception: The Directory ex/ at line 1 has at least two directories with same name. Name: a1/. First at line 2 and second one at line 5`

```
ex/
    a1/
        b/
            file_b1.txt
            file_b2.txt
            file_b3.txt
            file_b1.txt
```
`Exception: The Directory b/ at line 3 has at least two files with same name. Name: file_b1.txt. First at line 4 and second one at line 7`

# Examples

The following example will produce the same result and notice the indentation level where both files are.
```
ex1/
    a/ b/ c/
                file_c.txt
            file_b.txt
ex2/
    a/
        b/
            c/
                file_c.txt
            file_b.txt
```

Shortcut to create a deeper file in a nested directory. It's possible to extend that behavior with indent level of directories or files.

`input.txt`
```
ex1/
    a/
        b/
            file_b.txt

ex2/a/b/file_b.txt

ex3/a/b1/file_b1.txt
        b2/file_b2.txt
```

`output.sh`
```
mkdir -p {ex1,ex2,ex3}
mkdir -p ex1/a/b/
touch ex1/a/b/file_b.txt
mkdir -p ex2/a/b/
touch ex2/a/b/file_b.txt
mkdir -p ex3/a/{b1,b2}
touch ex3/a/b1/file_b1.txt
touch ex3/a/b2/file_b2.txt
```
