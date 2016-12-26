from __future__ import absolute_import
import re

IGNORE_CHARACTERS = u'\r\n\ \t'

IGNORE_REGEX = u'([\r\n\ \t]*)'
INTERVAL_REGEX = u'([\r\n\ \t]+)'

ESSENTIAL_REGEX = u'([' + IGNORE_CHARACTERS + u']*[^' + IGNORE_CHARACTERS + u'])'

INCLUDE_REGEX = u'(\#include' + IGNORE_REGEX + u'((\"[a-zA-Z0-9\/\.]+\")|(\<[a-zA-Z0-9\/\.]+\>))' + IGNORE_REGEX + u'\n)'

NAME_REGEX = u'([a-zA-Z\_][\w]*)'

TYPE_REGEX = u'(' + NAME_REGEX + u'(' + INTERVAL_REGEX + NAME_REGEX + u')*' + IGNORE_REGEX + u'[\*]*)'

RAW_DECIMAL_INTEGER_REGEX = u'((0)|([1-9][0-9]*))'
DECIMAL_INTEGER_REGEX = u'(([\+\-]?)' + RAW_DECIMAL_INTEGER_REGEX + u')'
RAW_HEX_INTEGER_REGEX = u'(0x[0-9a-fA-F]+)'
RAW_OCT_INTEGER_REGEX = u'(0[0-7]+)'
RAW_INTEGER_REGEX = u'(' + RAW_DECIMAL_INTEGER_REGEX + u'|(' + RAW_HEX_INTEGER_REGEX + u'|' + RAW_OCT_INTEGER_REGEX + u'))'
INTEGER_REGEX = u'(([\+\-]?)' + RAW_INTEGER_REGEX + u')'
FLOAT_REGEX = u'(([\+\-]?)(' + RAW_DECIMAL_INTEGER_REGEX + u'|((0?\.[0-9]+)|(' + \
              RAW_DECIMAL_INTEGER_REGEX + u'e' + DECIMAL_INTEGER_REGEX + u'))))'

NUMBER_REGEX = u'((' + INTEGER_REGEX + u'((([uUlL])|((ll)|(LL)))?))|(' + FLOAT_REGEX + u'((([fF])|(lf))?)))'

STRING_REGEX = u'(\"[^\"]*\")'
CHAR_REGEX = u'\'[^\']*\''

IF_HEADER_REGEX = u'(if' + IGNORE_REGEX + u'\()'
ELSE_HEADER_REGEX = u'(else[\W])'
FOR_HEADER_REGEX = u'(for' + IGNORE_REGEX + u'\()'
WHILE_HEADER_REGEX = u'(while' + IGNORE_REGEX + u'\()'
BREAK_REGEX = u'(' + IGNORE_REGEX + u'break' + IGNORE_REGEX + u'\;)'
CONTINUE_REGEX = u'(' + IGNORE_REGEX + u'continue' + IGNORE_REGEX + u'\;)'
RETURN_REGEX = u'(' + IGNORE_REGEX + u'return(' + INTERVAL_REGEX + u'|([\W])))'
VALIDATE_REGEX = u'(validate' + IGNORE_REGEX + u'\()'

NAME_HEADER_REGEX = u'(' + NAME_REGEX + u'[\W])'


def debug_print(s):
    print u'debug:  %s' % s


def debug_exit(v):
    exit(v)


def is_expression(s):
    i=0
    while re.match(u'^'+INTERVAL_REGEX,s[i:i+1]):
        i+=1
    s=s[i:]
    j=i
    while j<len(s) and (not (s[j] in IGNORE_CHARACTERS)):
        j+=1
    i=j
    while i<len(s) and (s[i] in IGNORE_CHARACTERS):
        i+=1
    if i<len(s):
        if re.match(u'^'+NAME_REGEX,s[j-1:j]) and re.match(u'^'+NAME_REGEX,s[i:i+1]):
            return False
    return True

