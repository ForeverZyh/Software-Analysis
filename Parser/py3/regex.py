import re

IGNORE_CHARACTERS = '\r\n\ \t'

IGNORE_REGEX = '([\r\n\ \t]*)'
INTERVAL_REGEX = '([\r\n\ \t]+)'

ESSENTIAL_REGEX = '([' + IGNORE_CHARACTERS + ']*[^' + IGNORE_CHARACTERS + '])'

INCLUDE_REGEX = '(\#include' + IGNORE_REGEX + '((\"[a-zA-Z0-9\/\.]+\")|(\<[a-zA-Z0-9\/\.]+\>))' + IGNORE_REGEX + '\n)'

NAME_REGEX = '([a-zA-Z\_][\w]*)'

TYPE_REGEX = '(' + NAME_REGEX + '(' + INTERVAL_REGEX + NAME_REGEX + ')*' + IGNORE_REGEX + '[\*]*)'

RAW_DECIMAL_INTEGER_REGEX = '((0)|([1-9][0-9]*))'
DECIMAL_INTEGER_REGEX = '(([\+\-]?)' + RAW_DECIMAL_INTEGER_REGEX + ')'
RAW_HEX_INTEGER_REGEX = '(0x[0-9a-fA-F]+)'
RAW_OCT_INTEGER_REGEX = '(0[0-7]+)'
RAW_INTEGER_REGEX = '(' + RAW_DECIMAL_INTEGER_REGEX + '|(' + RAW_HEX_INTEGER_REGEX + '|' + RAW_OCT_INTEGER_REGEX + '))'
INTEGER_REGEX = '(([\+\-]?)' + RAW_INTEGER_REGEX + ')'
FLOAT_REGEX = '(([\+\-]?)(' + RAW_DECIMAL_INTEGER_REGEX + '|((0?\.[0-9]+)|(' + \
              RAW_DECIMAL_INTEGER_REGEX + 'e' + DECIMAL_INTEGER_REGEX + '))))'

NUMBER_REGEX = '((' + INTEGER_REGEX + '((([uUlL])|((ll)|(LL)))?))|(' + FLOAT_REGEX + '((([fF])|(lf))?)))'

STRING_REGEX = '(\"[^\"]*\")'
CHAR_REGEX = '\'[^\']*\''

IF_HEADER_REGEX = '(if' + IGNORE_REGEX + '\()'
ELSE_HEADER_REGEX = '(else[\W])'
FOR_HEADER_REGEX = '(for' + IGNORE_REGEX + '\()'
WHILE_HEADER_REGEX = '(while' + IGNORE_REGEX + '\()'
BREAK_REGEX = '(' + IGNORE_REGEX + 'break' + IGNORE_REGEX + '\;)'
CONTINUE_REGEX = '(' + IGNORE_REGEX + 'continue' + IGNORE_REGEX + '\;)'
RETURN_REGEX = '(' + IGNORE_REGEX + 'return(' + INTERVAL_REGEX + '|([\W])))'

NAME_HEADER_REGEX = '(' + NAME_REGEX + '[\W])'


def debug_print(s):
    print('debug:  %s' % s)


def debug_exit(v):
    exit(v)


def is_expression(s):
    i=0
    while re.match('^'+INTERVAL_REGEX,s[i:i+1]):
        i+=1
    s=s[i:]
    j=i
    while j<len(s) and (not (s[j] in IGNORE_CHARACTERS)):
        j+=1
    i=j
    while i<len(s) and (s[i] in IGNORE_CHARACTERS):
        i+=1
    if i<len(s):
        if re.match('^'+NAME_REGEX,s[j-1:j]) and re.match('^'+NAME_REGEX,s[i:i+1]):
            return False
    return True

