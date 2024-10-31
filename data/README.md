# Donors for Debian Experiment
Here, we use simplified version of benchmark donor programs.\
This is, however, equivalent to the original one when pattern is abstracted.\
We do this for the sake of optimizing abstraction process\

## List of excluded benchmarks

The following benchmarks were excluded in the experiment due to the following reasons.\

patchweave-5: Uninitialized memory access -> can't analyze via taint analysis\
patchweave-7: duplicate to patchweave-1\
patchweave-10: relationship between sink expr and exprs used in patch is not shown within the program\
patchweave-11: duplicate to patchweave-6\
patchweave-13: too similar to patchweave-12\
patchweave-14: unclear patch\
patchweave-15: assertion failure\
patchweave-18: error not specified\
patchweave-19: duplicate to patchweave-3\
patchweave-20: control dependency error\
patchweave-21: memory write error\
patchweave-22: buffer overflow(not used for now)\
patchweave-23: buffer overflow(not used for now)\
patron-2: duplicate to patchweave-1\
patron-4: buffer overflow on fread(not used for now)\
patron-6: Pattern too simple, just one side of Mult-BinOP is tainted.\
patron-6: buffer overflow(not used for now)\
patron-7: pattern does not encode type -> won't catch similar pattern\
patron-8: pattern does not encode loop -> won't catch similar pattern\
patron-11: heap buffer overflow(not used for now)\
patron-12: Null Pointer Dereference(not used for now)\
patron-13: duplicate to patron-9\
patron-14: duplicate to patchweave-2\
patron-15: patch not generalizable (jas_alloc -> jas_alloc2)\
patron-15: pattern does not encode type -> won't catch similar pattern\
patron-17: pattern does not encode type -> won't catch similar pattern\
patron-18: pattern does not encode type -> won't catch similar pattern\
patron-19: pattern does not encode type -> won't catch similar pattern\

Here, duplicate does not mean it is same patch, but pattern comes out almost the same.

## List of additional benchmarks
CVE-2017-9181: Autotrace TIO bug from Tracer benchmark
