#!/usr/bin/env python

import StringIO
import pipes
import subprocess


class __SymTbl(object):
    def __init__(self):
        self.__undef_syms = set()
        self.__def_syms = set()
        pass

    def add_undefined(self, sym):
        self.__undef_syms.add(sym)
        pass

    def add_defined(self, sym):
        self.__def_syms.add(sym)
        pass

    def undefined(self):
        return self.__undef_syms

    def defined(self):
        return self.__def_syms

    def __str__(self):
        sio = StringIO.StringIO()
        print >> sio, "Symbol Table"

        print >> sio, "Undefined: {}".format(len(self.__undef_syms))
        for each in self.__undef_syms:
            print >> sio, "    ", each

        print >> sio, "Defined: {}".format(len(self.__def_syms))
        for each in self.__def_syms:
            print >> sio, "    ", each

        return sio.getvalue()


def get_symtbl(binary):
    """
    Raise exception with failure reason when failed to run nm.
    """
    ## Get nm output
    cmd = 'nm --extern-only {}'.format(pipes.quote(binary))
    # When check_output failed, subprocess.CalledProcessError will be raised
    nm_out = subprocess.check_output(cmd, shell=True)

    sym_tbl = __SymTbl()
    ## Get defined / undefined symbols from nm
    for each in nm_out.splitlines():
        fields = each.split()
        if len(fields) == 2:
            ty = fields[0]
            sym = fields[1]
        elif len(fields) == 3:
            ty = fields[1]
            sym = fields[2]
        else:
            continue

        if ty == 'U':
            sym_tbl.add_undefined(sym)
        else:
            sym_tbl.add_defined(sym)

    return sym_tbl

def resolve(main_obj, libs):
    """
    Return a list of libraries in correct order that are dependencies of the main object file.
    If libraries has dependencies, their dependencies are also resolved.
    """
    # FIXME: FINISH THIS
    pass
