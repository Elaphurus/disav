import sys, time, struct, marshal, dis, types

MAGIC_TAG = {
    # Python 1
    20121: (1, 5),
    50428: (1, 6),

    # Python 2
    50823: (2, 0),
    60202: (2, 1),
    60717: (2, 2),
    62011: (2, 3),  # a0
    62021: (2, 3),  # a0
    62041: (2, 4),  # a0
    62051: (2, 4),  # a3
    62061: (2, 4),  # b1
    62071: (2, 5),  # a0
    62081: (2, 5),  # a0
    62091: (2, 5),  # a0
    62092: (2, 5),  # a0
    62101: (2, 5),  # b3
    62111: (2, 5),  # b3
    62121: (2, 5),  # c1
    62131: (2, 5),  # c2
    62151: (2, 6),  # a0
    62161: (2, 6),  # a1
    62171: (2, 7),  # a0
    62181: (2, 7),  # a0
    62191: (2, 7),  # a0
    62201: (2, 7),  # a0
    62211: (2, 7),  # a0

    # Python 3
    3000: (3, 0),
    3010: (3, 0),
    3020: (3, 0),
    3030: (3, 0),
    3040: (3, 0),
    3050: (3, 0),
    3060: (3, 0),
    3061: (3, 0),
    3071: (3, 0),
    3081: (3, 0),
    3091: (3, 0),
    3101: (3, 0),
    3103: (3, 0),
    3111: (3, 0),  # a4
    3131: (3, 0),  # a5

    # Python 3.1
    3141: (3, 1),  # a0
    3151: (3, 1),  # a0

    # Python 3.2
    3160: (3, 2),  # a0
    3170: (3, 2),  # a1
    3180: (3, 2),  # a2

    # Python 3.3
    3190: (3, 3),  # a0
    3200: (3, 3),  # a0
	3210: (3, 3),  # a1
    3220: (3, 3),  # a1
    3230: (3, 3),  # a4

    # Python 3.4
    3250: (3, 4),  # a1
    3260: (3, 4),  # a1
    3270: (3, 4),  # a1
    3280: (3, 4),  # a1
    3290: (3, 4),  # a4
    3300: (3, 4),  # a4
    3310: (3, 4),  # rc2

    # Python 3.5
    3320: (3, 5),  # a0
    3330: (3, 5),  # b1
    3340: (3, 5),  # b2
    3350: (3, 5),  # b2
    3351: (3, 5),  # 3.5.2

    # Python 3.6
    3360: (3, 6),  # a0
    3361: (3, 6),  # a0
    3370: (3, 6),  # a1
    3371: (3, 6),  # a1
    3372: (3, 6),  # a1
    3373: (3, 6),  # b1
    3375: (3, 6),  # b1
    3376: (3, 6),  # b1
    3377: (3, 6),  # b1
    3378: (3, 6),  # b2
    3379: (3, 6),  # rc1

    # Python 3.7
    3390: (3, 7),  # a1
    3391: (3, 7),  # a2
    3392: (3, 7),  # a4
    3393: (3, 7),  # b1
    3394: (3, 7),  # b5

	# Python 3.8
	3400: (3, 8),  # a1
	3401: (3, 8),  # a1
	3411: (3, 8),  # b2
	3412: (3, 8),  # b2
	3413: (3, 8),  # b4

	# Python 3.9
	3420: (3, 9),  # a0
	3421: (3, 9),  # a0
	3422: (3, 9),  # a0
	3423: (3, 9),  # a2
	3424: (3, 9),  # a2
	3425: (3, 9),  # a2
}

def magic_to_version(magic):
    magic_decimal = struct.unpack('<H', magic)[0]
    return MAGIC_TAG[magic_decimal]

def bytes_to_dec(b):
	return struct.unpack('<L', b)[0] # little-endian

def show_hex(label, h, indent):
    h = h.hex()
    if len(h) < 60:
        print("{}{} {}".format(indent, label, h))
    else:
        print("{}{}".format(indent, label))
        for i in range(0, len(h), 60):
            print("{}   {}".format(indent, h[i:i+60]))

def show_code(code, indent=''):
    print("{}code".format(indent))
    indent += '   '
    print("{}argcount {}".format(indent, code.co_argcount))
    print("{}nlocals {}".format(indent, code.co_nlocals))
    print("{}stacksize {}".format(indent, code.co_stacksize))
    print("{}flags {:0>4d}".format(indent, code.co_flags))
    show_hex("code", code.co_code, indent=indent)
    dis.dis(code)
    print("{}consts".format(indent))
    for const in code.co_consts:
        if type(const) == types.CodeType:
            show_code(const, indent+'   ')
        else:
            print("   {}{}".format(indent, const))
    print("{}names {}".format(indent, code.co_names))
    print("{}varnames {}".format(indent, code.co_varnames))
    print("{}freevars {}".format(indent, code.co_freevars))
    print("{}cellvars {}".format(indent, code.co_cellvars))
    print("{}filename {}".format(indent, code.co_filename))
    print("{}name {}".format(indent, code.co_name))
    print("{}firstlineno {}".format(indent, code.co_firstlineno))
    show_hex("lnotab", code.co_lnotab, indent=indent)

def show_moddate(moddate):
    modtime = bytes_to_dec(moddate)
    print("moddate {} ({}, {})".format(moddate.hex(), modtime, time.asctime(time.localtime(modtime))))

def show_filesize(filesize):
    print("size {} ({}B)".format(filesize.hex(), bytes_to_dec(filesize)))

def disassemble(pyc_file):
    with open(pyc_file, 'rb') as f:
        # magic number
        magic_version = f.read(2)
        magic_tail    = f.read(2)
        python_version = magic_to_version(magic_version)
        print("magic {}{} {}".format(magic_version.hex(), magic_tail.hex(), python_version))

        if python_version[0] == 2:
            # TODO
            pass
        else:
            minor_version = python_version[1]
            # < 3.3
            if minor_version < 3:
                # timestamp
                moddate = f.read(4)
                show_moddate(moddate)
            # [3.3, 3.7)
            elif minor_version < 7:
                # timestamp
                moddate = f.read(4)
                show_moddate(moddate)
                # file size
                filesize = f.read(4) # 32-bit file size
                show_filesize(filesize)
            # >= 3.7
            else:
                # bit field
                field = f.read(4)
                print("field {}".format(field.hex()))
                if field.hex()[7] == '0': # lowest bit (big-endian)
                    # timestamp
                    moddate = f.read(4)
                    show_moddate(moddate)
                    # file size
                    filesize = f.read(4) # 32-bit file size
                    show_filesize(filesize)
                else:
                    # hash TODO
                    hash = f.read(8) # 64-bit hash of the source file

            # code
            code = marshal.load(f)
            show_code(code)

            return (code, python_version)

if __name__ == '__main__':
    pyc_file = sys.argv[1]
    disassemble(pyc_file)
