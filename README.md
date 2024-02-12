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
ex/
    {file1_ex.txt, file2_ex.txt, module1/, module2/src/file_module2.txt, module3/{file_module3.txt, inner/src/{file1_inner.txt, file2_inner.txt}}}

README.md
```

`output.sh`
```
mkdir -p {javascript,ex}
mkdir -p javascript/modules/{lib1,lib2,lib3}
touch javascript/modules/lib1/index.js
mkdir -p javascript/modules/lib2/src/
touch javascript/modules/lib2/src/index.js
mkdir -p javascript/modules/lib3/{src,modules}
touch javascript/modules/lib3/src/index.js
touch javascript/{index.js,timer.js,stuff.js}
mkdir -p ex/{module1,module2,module3}
mkdir -p ex/module2/src/
touch ex/module2/src/file_module2.txt
mkdir -p ex/module3/inner/src/
touch ex/module3/inner/src/{file1_inner.txt,file2_inner.txt}
touch ex/module3/file_module3.txt
touch ex/{file1_ex.txt,file2_ex.txt}
```

# Explaining the syntax

- Indentation will determine where directories and files will be placed.
- Every directory should end with an `/`.
- Comments starts with `--` and should be make in a empty line or in the end of line.

## usage
```sh
python mktree.py -f input.txt
python mktree.py -f input.txt -o output.sh -save --indent 4
python mktree.py -i "src/{index.html, css/styles.css, index.js}"
```

## Commands

- `-i`, `--input`: input txt
- `-f`, `--file`: file input txt filename
- `-o`, `--output`: output script filename. Default: `output.sh`
- `--indent`: indent size of directories and files. That's not strict, it's possible to multiples of the indent value.
- `--save`: Save
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

Extends error
```
ex/src/{file} -- WRONG Will not create the directories and file
ex/src/{file,} -- Correct
```

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

It's possible to create more than one file/directory per line. You can't newline when `{...}`.

`input`
```
src/{index.js, css/styles.css, module/inner_folder/{index.js, css/styles.css}}
```

`output`
```
mkdir -p src/{css,module}
touch src/css/styles.css
mkdir -p src/module/inner_folder/css/
touch src/module/inner_folder/css/styles.css
touch src/module/inner_folder/index.js
touch src/index.js
```

Another example

`input.txt`
```
ex1/
    index.html
    module1/
        index.js
        styles.css
    index.js
    module2/
        module2_src.js
        file/
            src/
                index.js
                styles.css

ex2/
    {index.html, module1/{index.js, styles.css}, index.js, module2/{module2_src.js, file/src/{index.js, styles.css}}}
```

`output.sh`
```
mkdir -p {ex1,ex2}
mkdir -p ex1/{module1,module2}
touch ex1/module1/{index.js,styles.css}
mkdir -p ex1/module2/file/src/
touch ex1/module2/file/src/{index.js,styles.css}
touch ex1/module2/module2_src.js
touch ex1/{index.html,index.js}
mkdir -p ex2/{module1,module2}
touch ex2/module1/{index.js,styles.css}
mkdir -p ex2/module2/file/src/
touch ex2/module2/file/src/{index.js,styles.css}
touch ex2/module2/module2_src.js
touch ex2/{index.html,index.js}
```
