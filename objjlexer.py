#!/usr/bin/env python

import ply.yacc as yacc
import objjtokenizer

class ObjJLexer(object):
    def __init__(self):
        self.classes = []
    
    def print_class(self, c):
        print "Class %s : %s" % (c['name'], c['super'])
        for s in c['selectors']:
            print "  %s(%s)%s" % (s['type'], s['returns'], s['name'])
    
    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)
        l = objjtokenizer.ObjJTokenizer()
        l.build()
        self.lexer = l

    def test(self, data):
        import logging
        logging.basicConfig(
            level = logging.DEBUG,
            filename = "parselog.txt",
            filemode = "w",
            format = "%(filename)10s:%(lineno)4d:%(message)s"
        )
        log = logging.getLogger()
        return self.parser.parse(data, debug=log)

    tokens = objjtokenizer.ObjJTokenizer.tokens
    
    def p_classes(self, p):
        '''classes : class
                   | classes class'''
    
    def p_class(self, p):
        'class : class_header class_methods KWEND'
        self.classes.append({
            'name': p[1][0],
            'super': p[1][1],
            'selectors': p[2],
        })
    
    def p_class_error(self, p):
         'class : class_header class_methods KWEND error'
         self.classes.append({
             'name': p[1][0],
             'super': p[1][1],
             'selectors': p[2],
         })
         print "Garbage after class definition:", p[4]
    
    def p_class_header(self, p):
        '''class_header : KWIMPLEMENTATION IDENTIFIER COLON IDENTIFIER
                        | KWIMPLEMENTATION IDENTIFIER BRACE_OPEN IDENTIFIER BRACE_CLOSE
                        | KWIMPLEMENTATION IDENTIFIER'''
        if   len(p) == 5:
            p[0] = (p[2], p[4])
        elif len(p) == 6:
            p[0] = ('%s(%s)' % (p[2], p[4]), None)
        else:
            p[0] = (p[2], None)
    
    def p_class_methods(self, p):
        '''class_methods : class_method
                         | class_methods class_method'''
        if len(p) == 2:
            p[0] = [p[1],]
        else:
            p[1].append(p[2])
            p[0] = p[1]
    
    def p_class_method(self, p):
        'class_method : METHOD_TYPE BRACE_OPEN IDENTIFIER BRACE_CLOSE selector'
        p[0] = {
            'type': p[1],
            'returns': p[3],
            'name': p[5],
        }
    
    def p_selector(self, p):
        '''selector : selector_args VARGS
                    | selector_args
                    | selector_noargs'''
        if len(p) == 3:
            p[0] = p[1] + ',...'
        else:
            p[0] = p[1]
    
    def p_selector_noargs(self, p):
        'selector_noargs : IDENTIFIER'
        p[0] = p[1]
    
    def p_selector_args(self, p):
        '''selector_args : selector_part
                         | selector_args selector_part'''
        if(len(p) == 2):
            p[0] = p[1]
        else:
            p[0] = p[1] + ' ' + p[2]
    
    def p_selector_part(self, p):
        'selector_part : SELIDENTIFIER BRACE_OPEN IDENTIFIER BRACE_CLOSE IDENTIFIER'
        p[0] = '%s:(%s)%s' % (p[1], p[3], p[5])
    
    def p_error(self, p):
        print "Syntax error in input:",p
    
if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        tgt = 'Foundation/CPArray.j'
    else:
        tgt = sys.argv[1]
    l = ObjJLexer()
    l.build()
    l.test(objjtokenizer.cpp_and_open(tgt))
    for c in l.classes:
        l.print_class(c)
