from __future__ import with_statement
from __future__ import absolute_import
from cparser import car, cdr, generator, cparser
from expr import Expr
import sys

import re
from io import open

IGNORE_CHARACTERS = u'\r\n\ \t'

IGNORE_REGEX = u'([\r\n\ \t]*)'
INTERVAL_REGEX = u'([\r\n\ \t]+)'

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

u"""
graph = cparser(text)
"""
can_parallel = []
alter = []

long = u"#pragma acc parallel loop"
short = u"#pragma acc loop"
countfor = 0


def parse_block(begin, end, outer_new, for_father, outer_end):
    global countfor
    whole = Expr(u"")
    (values, arrays) = car(begin.env)
    while 1:
        if begin.category != u"for":
            whole.merge(begin.expression)
        if begin.category == u"for":
            if for_father:
                for_father.son.append(begin)
            else:
                graph.begin.son.append(begin)
            tmp = Expr(u"")
            exp = begin.succ_inst[0]
            t = 0
            if exp.succ_inst[0] == begin.jump:
                t = 1
            q = 0
            if exp.pred_inst[0] == begin:
                q = 1
            new = exp.pred_inst[q]
            if len(new.pred_inst) > 1:
                tmp.interrupt = True
            for i in xrange(len(new.pred_inst)):
                if len(new.pred_inst[i].succ_inst)==1:
                    tmp.merge(parse_block(exp.succ_inst[t], new.pred_inst[i], new, begin, begin.jump))
            begin.isLikely = isLikely(begin.expression.s, exp.expression.s, new.expression.s)
            itr = None
            if begin.isLikely:
                itr = begin.expression.Var_Mdf[0]
            begin.expression.merge(tmp)
            if itr:
                while itr in begin.expression.Var_Mdf:
                    begin.expression.Var_Mdf.remove(itr)
                countfor += 1
                for i in xrange(len(begin.expression.Array_Mdf)):
                    for j in xrange(len(begin.expression.Array_Mdf[i][1])):
                        if begin.expression.Array_Mdf[i][1][j] == itr:
                            begin.expression.Array_Mdf[i][1][j] += unicode(countfor) + u"@Software"
                for i in xrange(len(begin.expression.Array_Use)):
                    for j in xrange(len(begin.expression.Array_Use[i][1])):
                        if begin.expression.Array_Use[i][1][j] == itr:
                            begin.expression.Array_Use[i][1][j] += unicode(countfor) + u"@Software"
            if itr in begin.jump.live.live:
                begin.isLikely = False
            # print(begin.line)
            # # print(begin.isLikely)
            # # print(begin.expression.interrupt)
            # begin.expression.printf()
            # print(isParallel(begin, begin.jump))
            add = isParallel(begin, begin.jump)
            if not (add is False):
                can_parallel.append([begin, add])
            whole.merge(begin.expression)
            begin = begin.jump
        elif begin.category == u"if":
            whole.merge(parse_block(begin.succ_inst[0], begin.jump, outer_new, for_father, outer_end))
            whole.merge(parse_block(begin.succ_inst[1], begin.jump, outer_new, for_father, outer_end))
            begin = begin.jump
        elif begin.category == u"while":
            if begin == end:
                break
            t = 0
            if begin.succ_inst[0] == begin.jump:
                t = 1
            whole.merge(parse_block(begin.succ_inst[t], begin, begin, for_father, begin.jump))
            begin = begin.jump
        if begin == end:
            break
        if len(begin.succ_inst) > 2:
            print u"Error!"
        elif len(begin.succ_inst) > 1:
            whole.interrupt = True
            if graph.end in begin.succ_inst:
                print u"return"
                t = 1 - begin.succ_inst.index(graph.end)
                begin = begin.succ_inst[t]
            else:
                t = 0
                if begin.succ_inst[0].expression.s == u"":
                    t = 1
                if begin.succ_inst[t].expression.s != u"":
                    print u"continue"
                    if begin.succ_inst[t] == outer_new:
                        t = 1 - t
                    begin = begin.succ_inst[t]
                else:
                    print u"break"
                    begin = begin.succ_inst[t]

        else:
            begin = begin.succ_inst[0]
    for i in xrange(len(values)):
        tmp = []
        for j in xrange(len(whole.Var_Rdc)):
            if values[i] != whole.Var_Rdc[j][0]:
                tmp.append(whole.Var_Rdc[j])
        whole.Var_Rdc = tmp
        while values[i] in whole.Var_Use:
            whole.Var_Use.remove(values[i])
        while values[i] in whole.Var_Mdf:
            whole.Var_Mdf.remove(values[i])
    return whole


def eliminate(pre, ins, li):
    ans = []
    for i in xrange(len(li)):
        ans.append(li[i])
    X = ins.env
    Y = pre.env
    x = len(list(generator(X)))
    y = len(list(generator(Y)))
    while 1:
        if x == y and X == Y:
            break
        if x >= y:
            (values, arrays) = car(X)
            x -= 1
            for i in xrange(len(values)):
                if values[i] in ans:
                    ans.remove(values[i])
            X = cdr(X)
        else:
            y -= 1
            Y = cdr(Y)
    return ans


def Downwards_Analysis(begin, end):
    h = [end]
    t = 0
    w = 1
    while t < w:
        ins = h[t]
        ins.expression.parse()
        t += 1
        l = len(ins.pred_inst)
        for i in xrange(l):
            pre = ins.pred_inst[i]
            if not (pre in h):
                h.append(pre)
                w += 1
    t = 0
    while t < w:
        ins = h[t]
        t += 1
        pre = []
        for i in xrange(len(ins.live.live)):
            pre.append(ins.live.live[i])
        ins.live.gen(ins.expression.Var_Use)
        ins.live.kill(ins.expression.Var_Mdf)
        # print(ins.expression.s)
        # print(ins.live.live)
        if ins.live.isUpdate(pre) and ins != begin:
            l = len(ins.pred_inst)
            for i in xrange(l):
                pre = ins.pred_inst[i]
                clear_live = eliminate(pre, ins, ins.live.live)
                pre.live.gen(clear_live)
                if not (pre in h[t:w]):
                    h.append(pre)
                    w += 1


def isLikely(_init, _pred, _new):
    init = Expr(_init)
    init.parse()
    pred = Expr(_pred)
    pred.parse()
    new = Expr(_new)
    new.parse()
    if len(init.Array_Mdf) == 0 and len(init.Var_Mdf) == 1:
        if len(new.Var_Rdc) == 1 and ((new.Var_Rdc[0][1] == u"++" or new.Var_Rdc[0][1] == u"--") or (
                            len(new.var) == 2 and new.fa[0][0] in u"+-" and (new.var[0] is None or new.var[1] is None))):
            if len(pred.Var_Use) <= 2 and init.Var_Mdf[0] in pred.Var_Use:
                return True
    return False


def isParallel(begin, end):
    if begin.category == u"for" and begin.jump == end and begin.isLikely and not begin.expression.interrupt:
        # print("===",begin.line)
        Rdc = []
        for i in xrange(len(begin.expression.Var_Mdf)):
            obj = begin.expression.Var_Mdf[i]
            t = begin.expression.Var_Mdf.count(obj)
            op = None
            for j in xrange(len(begin.expression.Var_Rdc)):
                cmp = begin.expression.Var_Rdc[i]
                if cmp[0] == obj:
                    t -= 1
                    if op:
                        if op != cmp[1]:
                            return False
                    else:
                        op = cmp[1]
            if t != 0:
                return False
            if not ([obj, op] in Rdc):
                Rdc.append([obj, op])

        for i in xrange(len(begin.expression.Array_Mdf)):
            for j in xrange(len(begin.expression.Array_Use)):
                obj1 = begin.expression.Array_Mdf[i]
                obj2 = begin.expression.Array_Use[j]
                if obj1[0] == obj2[0]:
                    l = len(obj1)
                    if l != len(obj2):
                        print u"Error!"
                        return False
                    for k in xrange(l):
                        if obj1[k] != obj2[k]:
                            return False
        return Rdc
    return False


def is_expression(s):
    i = 0
    while re.match(u'^' + INTERVAL_REGEX, s[i:i + 1]):
        i += 1
    s = s[i:]
    j = i
    while j < len(s) and (not (s[j] in IGNORE_CHARACTERS)):
        j += 1
    i = j
    while i < len(s) and (s[i] in IGNORE_CHARACTERS):
        i += 1
    if i < len(s):
        if re.match(u"^" + NAME_REGEX, s[j - 1:j]) and re.match(u"^" + NAME_REGEX, s[i:i + 1]):
            return False
    return True


def find(begin):
    for i in xrange(len(can_parallel)):
        if can_parallel[i][0] == begin:
            return can_parallel[i][1]
    return False


def change(s):
    if (s == u"fmax"):
        return u"max"
    if (s == u"fmin"):
        return u"min"
    return s


def dfs(begin, flag):
    # print(begin.line, "(")
    t = find(begin)
    if begin.line > 0 and not (t is False):
        if not flag:
            s = long
        else:
            s = short
        for i in xrange(len(t)):
            s += u" reduction(" + change(t[i][1]) + u":" + t[i][0] + u")"
        s += u"\n"
        alter.append([begin.line, s])
        flag = True
    for i in xrange(len(begin.son)):
        dfs(begin.son[i], flag)
        # print(")")


def write(now):
    for i in xrange(len(alter)):
        if alter[i][0] == now:
            fout.write(alter[i][1])


Test = False
if len(sys.argv) == 3 or Test:
    if Test:
        filein = u"sample2.c"
        fileout = u"new2.c"
    else:
        filein = sys.argv[1]
        fileout = sys.argv[2]
    with open(filein, u'r') as fin:
        graph = cparser(fin.read())
    Downwards_Analysis(graph.begin, graph.end)
    parse_block(graph.begin, graph.end, None, None, None)
    graph.begin.line = 0
    dfs(graph.begin, False)
    now = 0
    with open(fileout, u'w') as fout:
        with open(filein, u'r') as fin:
            while 1:
                s = fin.readline()
                if s:
                    now += 1
                    write(now)
                    fout.write(s)
                else:
                    break
else:
    print u"Usage : analysis.py <infile> <outfile>"
