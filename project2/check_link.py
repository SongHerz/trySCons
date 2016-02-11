#!/usr/bin/env python

import buildhelper.linkdep as ld

# print ld.get_symtbl('obj/ut/libut.a')
print ld.resolve('obj/prog_cir.o', ['obj/cir0/libcir0.a', 'obj/cir1/libcir1.a', 'obj/ut/libut.a', 'obj/util/libutil.a', 'obj/common/libcommon.a'], True)
