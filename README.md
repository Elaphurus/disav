# Python Bytecode Disassembler

## Python Bytecode

### Code Object

```
>>> def func(x):
...     x *= -1
...     return x
>>> func.__code__
<code object func at 0x10cdadc00, file "<stdin>", line 1>
>>> func.__code__.co_code
b'|\x00d\x019\x00}\x00|\x00S\x00’
>>> import dis
>>> dis.dis(func.__code__.co_code)
          0 LOAD_FAST                0 (0)
          2 LOAD_CONST               1 (1)
          4 INPLACE_MULTIPLY
          6 STORE_FAST               0 (0)
          8 LOAD_FAST                0 (0)
         10 RETURN_VALUE
>>> func.__code__.co_consts
(None, -1)
```

### .pyc File

```
>>> import py_compile
>>> py_compile.compile("test.py")
'__pycache__/test.cpython-37.pyc'
```

.pyc files are independent of platform, but very sensitive to Python versions.

__< 3.3__ [1]

- 4B magic number versioning the bytecode and pyc format
- 4B modification timestamp
- Marshalled code object (`co_code`)

__[3.3, 3.7)__, since PEP 3147 -- PYC Repository Directories [2]

- 4B magic number
- 4B modification timestamp
- 4B file size
- Marshalled code object

__>= 3.7__, since PEP 552 -- Deterministic pycs [3]

- 4B magic number
- 4B bit field
- ...

If the bit field is 0, the pyc is a traditional __timestamp-based pyc__. I.e., the third and forth words will be the timestamp and file size respectively, and invalidation will be done by comparing the metadata of the source file with that in the header.

- ...
- 4B modification timestamp
- 4B file size
- Marshalled code object

If the lowest bit of the bit field is set, the pyc is a __hash-based pyc__. We call the second lowest bit the check_source flag. Following the bit field is a 64-bit hash of the source file.

- ...
- 8B hash of the source file
- Marshalled code object

![](./fig/4-0.png)

__bytes to long__

E.g., the 4B modification timestamp is `b’/0\xd5]’`. 4 bytes are `/`, `0`, `\xd5`, `]` orderly, each of which maps to decimal `47`, `48`, `213`, `93` in extended ASCII table [4]. Thus the timestamp is `47 + 48 << 8 + 213 << 16 + 93 << 24 = 1574252591`, which is `Wed Nov 20 20:23:11 2019`.

Bytes to decimal long can be done with module `struct` [5]:

```python
struct.unpack('<L', b)[0]
```

## Disassembler for all Python versions

Source code: [GitHub](https://github.com/Elaphurus/disav) [11]

__CPython version__ 4B magic number contains:

- two bytes version: unique in each version of the Python interpreter
- two bytes of 0d0a: carriage return (CR) and line feed (LF), will change when a .pyc file is processed as text (copy corruption)

E.g., `420d = 66 + 13 << 8 = 3394`, `3394` maps to `Python 3.7b5`, key-value table can be found `cpython/Lib/importlib/_bootstrap_external.py` [6]. We implement the table mapping referring to google/pytype [7] (add 3210 and Python 3.8, 3.9).

__Bytecode__ Body of a .pyc file is just the output of `marshal.dump` of the code object that results from compiling the source file. After dealing with `marshal` [8] and `dis` [9] module, the byte codes are nicely disassembled and presented symbolically. We can further dump the attributes of `code` type referring to the document of `inspect` module [10].

## References

1. The structure of .pyc files, https://nedbatchelder.com/blog/200804/the_structure_of_pyc_files.html
2. PEP 3147 -- PYC Repository Directories, https://www.python.org/dev/peps/pep-3147/
3. PEP 552 -- Deterministic pycs, https://www.python.org/dev/peps/pep-0552/
4. ASCII Code - The extended ASCII table, https://www.ascii-code.com
5. struct — Interpret bytes as packed binary data, https://docs.python.org/3.8/library/struct.html
6. cpython/Lib/importlib/_bootstrap_external.py, https://github.com/python/cpython/blob/master/Lib/importlib/_bootstrap_external.py
7. google/pytype/pytype/pyc/magic.py, https://github.com/google/pytype/blob/master/pytype/pyc/magic.py
8. marshal, https://docs.python.org/3.8/library/marshal.html
9. dis, https://docs.python.org/3.8/library/dis.html
10. inspect — Inspect live objects, https://docs.python.org/3.7/library/inspect.html#types-and-members
11. disav, https://github.com/Elaphurus/disav

---

Zhenjiang, 11 February 2020

Mingzhe Hu

School of Cyberspace Security

University of Science and Technology of China

hmz18@mail.ustc.edu.cn
