from objjlexer import ObjJLexer

def parse(fn):
    import objjtokenizer
    l = ObjJLexer()
    l.build()
    l.test(objjtokenizer.cpp_and_open(fn))
    return l.classes
