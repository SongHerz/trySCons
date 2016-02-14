#!/usr/bin/env python

import StringIO
import subprocess
import itertools

from .containers import OrderedSet


class _SymTbl(object):
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

    def is_undefined_defined_in(self, another):
        """
        Return True, if at least one undefined symbol defined in another symtbl.
               False, otherwise.
        """
        assert isinstance(another, _SymTbl)
        return any(itertools.imap(lambda u: u in another.defined(), self.undefined()))

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


def _get_symtbl(binary):
    """
    Raise exception with failure reason when failed to run nm.
    """
    ## Get nm output
    cmd_args = ['nm', '--extern-only', binary]
    # When check_output failed, subprocess.CalledProcessError will be raised
    nm_out = subprocess.check_output(cmd_args)

    sym_tbl = _SymTbl()
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


class _LinkDep(object):
    """
    Present dependency relations of objects/libraries.
    """
    def __init__(self, file_):
        """
        On initialize, it only contains information of the given file.
        Dependencies should be resolved later.
        """
        self.__file = file_
        self.__symtbl = _get_symtbl(self.__file)
        # Set(_LinkDep)
        self.__deps = OrderedSet()
        pass

    def _resolve_dep(self, link_deps):
        """
        Resolve dependencies with other _LinkDep instances.
        This is intended to be called by the dependency resolving algorithm.
        """
        for each in link_deps:
            if self.__symtbl.is_undefined_defined_in(each.__symtbl):
                self.__deps.add(each)
        pass

    def file_path(self):
        return self.__file

    def dependencies(self):
        return self.__deps

    def __str__(self):
        return "LinkDep({}, [{}])".format(
                self.file_path(),
                ', '.join(map(lambda ld: ld.file_path(), self.dependencies())))


def _int_flatten_deps(parent_lds, current_ld, ret):
    assert isinstance(parent_lds, OrderedSet)
    assert isinstance(current_ld, _LinkDep)
    assert isinstance(ret, list)

    if current_ld in parent_lds:
        print "Warning: Circular dependency detected for '{}', dependency chain '{}'".format(
            current_ld.file_path(), ', '.join(map(lambda ld: ld.file_path(), list(parent_lds) + [current_ld])))
        return

    ret.append(current_ld)
    parent_lds.add(current_ld)

    for each in current_ld.dependencies():
        _int_flatten_deps(parent_lds, each, ret)

    parent_lds.pop()
    pass

def _flatten_deps(main_obj_ld):
    """
    Return [_LinkDep] with given resolved main_obj_ld instance.
    NOTE: circular dependencies not supported.
    """
    assert isinstance(main_obj_ld, _LinkDep)
    ret = []
    _int_flatten_deps(OrderedSet(), main_obj_ld, ret)
    return ret

def resolve(main_obj, libs, show_detail=False):
    """
    Return a list of libraries in correct order that are dependencies of the main object file.
    If libraries has dependencies, their dependencies are also resolved.
    NOTE: May have problem on circular dependencies.
    """
    # ld is short for link_dep
    main_ld = _LinkDep(main_obj)
    other_lds = map(_LinkDep, libs)
    all_lds = [main_ld]
    all_lds.extend(other_lds)

    # Resolve for all lds
    for each in all_lds:
        each._resolve_dep(filter(lambda ld: each is not ld, all_lds))

    # Print dependencies for all lds
    if show_detail:
        for each in all_lds:
            print each

    # Collect dependencies from the main_obj
    flatten_res = _flatten_deps(main_ld)
    if show_detail:
        print ', '.join(map(lambda ld: '{} <{}>'.format(ld.file_path(), hex(id(ld))) , flatten_res))

    # Minimal dependencies
    minimal_res = reversed(OrderedSet(reversed(flatten_res)))
    return map(lambda ld: ld.file_path(), minimal_res)
