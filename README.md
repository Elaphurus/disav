<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Python Bytecode Disassembler</title>
        
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Microsoft/vscode/extensions/markdown-language-features/media/markdown.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Microsoft/vscode/extensions/markdown-language-features/media/highlight.css">
        
        <style>
.task-list-item { list-style-type: none; } .task-list-item-checkbox { margin-left: -20px; vertical-align: middle; }
</style>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe WPC', 'Segoe UI', 'Ubuntu', 'Droid Sans', sans-serif;
                font-size: 14px;
                line-height: 1.6;
            }
        </style>
        
        
    </head>
    <body class="vscode-light">
        <h1 id="python-bytecode-disassembler">Python Bytecode Disassembler</h1>
<h2 id="python-bytecode">Python Bytecode</h2>
<h3 id="code-object">Code Object</h3>
<pre><code><code><div>&gt;&gt;&gt; def func(x):
...     x *= -1
...     return x
&gt;&gt;&gt; func.__code__
&lt;code object func at 0x10cdadc00, file &quot;&lt;stdin&gt;&quot;, line 1&gt;
&gt;&gt;&gt; func.__code__.co_code
b'|\x00d\x019\x00}\x00|\x00S\x00’
&gt;&gt;&gt; import dis
&gt;&gt;&gt; dis.dis(func.__code__.co_code)
          0 LOAD_FAST                0 (0)
          2 LOAD_CONST               1 (1)
          4 INPLACE_MULTIPLY
          6 STORE_FAST               0 (0)
          8 LOAD_FAST                0 (0)
         10 RETURN_VALUE
&gt;&gt;&gt; func.__code__.co_consts
(None, -1)
</div></code></code></pre>
<h3 id="pyc-file">.pyc File</h3>
<pre><code><code><div>&gt;&gt;&gt; import py_compile
&gt;&gt;&gt; py_compile.compile(&quot;test.py&quot;)
'__pycache__/test.cpython-37.pyc'
</div></code></code></pre>
<p>.pyc files are independent of platform, but very sensitive to Python versions.</p>
<p><strong>&lt; 3.3</strong> [1]</p>
<ul>
<li>4B magic number versioning the bytecode and pyc format</li>
<li>4B modification timestamp</li>
<li>Marshalled code object (<code>co_code</code>)</li>
</ul>
<p><strong>[3.3, 3.7)</strong>, since PEP 3147 -- PYC Repository Directories [2]</p>
<ul>
<li>4B magic number</li>
<li>4B modification timestamp</li>
<li>4B file size</li>
<li>Marshalled code object</li>
</ul>
<p><strong>&gt;= 3.7</strong>, since PEP 552 -- Deterministic pycs [3]</p>
<ul>
<li>4B magic number</li>
<li>4B bit field</li>
<li>...</li>
</ul>
<p>If the bit field is 0, the pyc is a traditional <strong>timestamp-based pyc</strong>. I.e., the third and forth words will be the timestamp and file size respectively, and invalidation will be done by comparing the metadata of the source file with that in the header.</p>
<ul>
<li>...</li>
<li>4B modification timestamp</li>
<li>4B file size</li>
<li>Marshalled code object</li>
</ul>
<p>If the lowest bit of the bit field is set, the pyc is a <strong>hash-based pyc</strong>. We call the second lowest bit the check_source flag. Following the bit field is a 64-bit hash of the source file.</p>
<ul>
<li>...</li>
<li>8B hash of the source file</li>
<li>Marshalled code object</li>
</ul>
<p><img src="file:////Users/hmz/Documents/HMZ/fig/4-0.png" alt=""></p>
<p><strong>bytes to long</strong></p>
<p>E.g., the 4B modification timestamp is <code>b’/0\xd5]’</code>. 4 bytes are <code>/</code>, <code>0</code>, <code>\xd5</code>, <code>]</code> orderly, each of which maps to decimal <code>47</code>, <code>48</code>, <code>213</code>, <code>93</code> in extended ASCII table [4]. Thus the timestamp is <code>47 + 48 &lt;&lt; 8 + 213 &lt;&lt; 16 + 93 &lt;&lt; 24 = 1574252591</code>, which is <code>Wed Nov 20 20:23:11 2019</code>.</p>
<p>Bytes to decimal long can be done with module <code>struct</code> [5]:</p>
<pre><code class="language-python"><div>struct.unpack(<span class="hljs-string">'&lt;L'</span>, b)[<span class="hljs-number">0</span>]
</div></code></pre>
<h2 id="disassembler-for-all-python-versions">Disassembler for all Python versions</h2>
<p>Source code: <a href="https://github.com/Elaphurus/disav">GitHub</a> [11]</p>
<p><strong>CPython version</strong> 4B magic number contains:</p>
<ul>
<li>two bytes version: unique in each version of the Python interpreter</li>
<li>two bytes of 0d0a: carriage return (CR) and line feed (LF), will change when a .pyc file is processed as text (copy corruption)</li>
</ul>
<p>E.g., <code>420d = 66 + 13 &lt;&lt; 8 = 3394</code>, <code>3394</code> maps to <code>Python 3.7b5</code>, key-value table can be found <code>cpython/Lib/importlib/_bootstrap_external.py</code> [6]. We implement the table mapping referring to google/pytype [7] (add 3210 and Python 3.8, 3.9).</p>
<p><strong>Bytecode</strong> Body of a .pyc file is just the output of <code>marshal.dump</code> of the code object that results from compiling the source file. After dealing with <code>marshal</code> [8] and <code>dis</code> [9] module, the byte codes are nicely disassembled and presented symbolically. We can further dump the attributes of <code>code</code> type referring to the document of <code>inspect</code> module [10].</p>
<h2 id="references">References</h2>
<ol>
<li>The structure of .pyc files, <a href="https://nedbatchelder.com/blog/200804/the_structure_of_pyc_files.html">https://nedbatchelder.com/blog/200804/the_structure_of_pyc_files.html</a></li>
<li>PEP 3147 -- PYC Repository Directories, <a href="https://www.python.org/dev/peps/pep-3147/">https://www.python.org/dev/peps/pep-3147/</a></li>
<li>PEP 552 -- Deterministic pycs, <a href="https://www.python.org/dev/peps/pep-0552/">https://www.python.org/dev/peps/pep-0552/</a></li>
<li>ASCII Code - The extended ASCII table, <a href="https://www.ascii-code.com">https://www.ascii-code.com</a></li>
<li>struct — Interpret bytes as packed binary data, <a href="https://docs.python.org/3.8/library/struct.html">https://docs.python.org/3.8/library/struct.html</a></li>
<li>cpython/Lib/importlib/_bootstrap_external.py, <a href="https://github.com/python/cpython/blob/master/Lib/importlib/_bootstrap_external.py">https://github.com/python/cpython/blob/master/Lib/importlib/_bootstrap_external.py</a></li>
<li>google/pytype/pytype/pyc/magic.py, <a href="https://github.com/google/pytype/blob/master/pytype/pyc/magic.py">https://github.com/google/pytype/blob/master/pytype/pyc/magic.py</a></li>
<li>marshal, <a href="https://docs.python.org/3.8/library/marshal.html">https://docs.python.org/3.8/library/marshal.html</a></li>
<li>dis, <a href="https://docs.python.org/3.8/library/dis.html">https://docs.python.org/3.8/library/dis.html</a></li>
<li>inspect — Inspect live objects, <a href="https://docs.python.org/3.7/library/inspect.html#types-and-members">https://docs.python.org/3.7/library/inspect.html#types-and-members</a></li>
<li>disav, <a href="https://github.com/Elaphurus/disav">https://github.com/Elaphurus/disav</a></li>
</ol>
<hr>
<p>Zhenjiang, 11 February 2020</p>
<p>Mingzhe Hu</p>
<p>School of Cyberspace Security</p>
<p>University of Science and Technology of China</p>
<p><a href="mailto:hmz18@mail.ustc.edu.cn">hmz18@mail.ustc.edu.cn</a></p>

    </body>
    </html>