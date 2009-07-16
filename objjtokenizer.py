#!/usr/bin/env python

import ply.lex as lex

def cpp_and_open(f):
    import commands
    return commands.getoutput('cpp -P %s' % f)

class ObjJTokenizer(object):
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok: break
            print tok
    
    tokens = (
        'NUMBER',
        'SELIDENTIFIER',
        'IDENTIFIER',
        'COMMENT',
        'CODEBLOCK_START',
        'CODEBLOCK_END',
        'STRING',
        'KWIMPLEMENTATION',
        'KWEND',
        'KWIMPORT',
        
        # impl
        'METHOD_TYPE',
        'BRACE_OPEN',
        'BRACE_CLOSE',
        'COLON',
        'VARGS',
        
        'WORD',
    )
    
    states = (
        ('impl', 'inclusive'),
        ('implsel', 'inclusive'),
        ('codeblock', 'exclusive'),
    )
    
    #implsel
    def t_implsel_CODEBLOCK_START(self, t):
        r'{'
        t.lexer.pop_state()
        t.lexer.push_state('codeblock')
    
    def t_implsel_SELIDENTIFIER(self, t):
        r':|[a-zA-Z_][a-zA-Z_0-9]+:'
        return t
    
    #impl
    def t_impl_METHOD_TYPE(self, t):
        r'\+|-'
        t.lexer.push_state('implsel')
        return t
    
    def t_BRACE_OPEN(self, t):
        r'\('
        return t
    
    def t_BRACE_CLOSE(self, t):
        r'\)'
        return t
    
    def t_implsel_VARGS(self, t):
        r',\s+...'
        return t

    def t_impl_COLON(self, t):
        r':'
        return t
    
    #codeblock
    def t_CODEBLOCK_START(self, t):
        r'{'
        t.lexer.push_state('codeblock')
        #return t
    
    def t_codeblock_CODEBLOCK_START(self, t):
        r'{'
        t.lexer.push_state('codeblock')
        #return t
    
    def t_codeblock_CODEBLOCK_END(self, t):
        r'}'
        t.lexer.pop_state()
        #return t
    
    def t_codeblock_error(self, t):
        t.lexer.skip(1)
    
    t_codeblock_ignore = ' \t\n'
    
    #generic
    def t_STRING(self, t):
        r'".+"' # TODO: worth extending
        t.value = t.value[1:-1]
        return t
        
    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]+'
        return t
    
    def t_KWIMPLEMENTATION(self, t):
        r'@implementation'
        t.lexer.push_state('impl')
        return t
        
    def t_KWEND(self, t):
        r'@end'
        t.lexer.pop_state()
        return t
    
    def t_KWIMPORT(self, t):
        r'@import\s+((".+")|(<.+>))'
        t.value = t.value[t.value.find('"')+1:-1]
        #return t
    
    def t_COMMENT(self, t):
        r'//.*'
        pass
    
    #def t_WORD(self, t):
    #    r'.+'
    #    pass
    
    t_ignore = " \t\n"
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        #print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

if __name__ == '__main__':
    l = ObjJTokenizer()
    l.build()
    l.test(cpp_and_open('Foundation/CPArray.j'))
