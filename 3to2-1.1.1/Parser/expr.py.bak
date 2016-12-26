import re

IGNORE_CHARACTERS = '\r\n\ \t'

IGNORE_REGEX = '([\r\n\ \t]*)'
INTERVAL_REGEX = '([\r\n\ \t]+)'

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
inf = 1000000


def count(s, c):
    cnt = 0
    for x in s:
        if x == c:
            cnt += 1
    return cnt


def jump_block(s, ex=''):
    parentheses = 0
    brace = 0
    bracket = 0
    single_quote = False
    double_quote = False
    for i in range(len(s)):
        c = s[i]
        # print(brace)
        if c == '\"':
            if not single_quote:
                double_quote ^= True
        elif c == '\'':
            if not double_quote:
                single_quote ^= True
        elif single_quote or double_quote:
            continue
        elif c in ex:
            if (brace == 0) and (bracket == 0) and (parentheses == 0) and (not single_quote) and not double_quote:
                return i
        elif c == '(':
            parentheses += 1
        elif c == ')':
            parentheses -= 1
            if parentheses == -1:
                return i
        elif c == '[':
            bracket += 1
        elif c == ']':
            bracket -= 1
            if bracket == -1:
                return i
        elif c == '{':
            brace += 1
        elif c == '}':
            brace -= 1
            if brace == -1:
                return i


class Expr:
    def __init__(self, S):
        self.s = S
        self.Array_Mdf = []
        self.Array_Use = []
        self.Var_Mdf = []
        self.Var_Use = []
        self.Var_Rdc = []
        self.isRange = 0
        self.cnt = 0
        self.fa = []
        self.var = []
        self.interrupt = False

    def printf(self):
        print("Array_Mdf")
        l = len(self.Array_Mdf)
        for i in range(l):
            print(self.Array_Mdf[i])
        print("Array_Use")
        l = len(self.Array_Use)
        for i in range(l):
            print(self.Array_Use[i])
        print("Var_Mdf")
        l = len(self.Var_Mdf)
        for i in range(l):
            print(self.Var_Mdf[i])
        print("Var_Use")
        l = len(self.Var_Use)
        for i in range(l):
            print(self.Var_Use[i])
        print("Var_Rdc")
        l = len(self.Var_Rdc)
        for i in range(l):
            print(self.Var_Rdc[i])

    def parse_var(self, s):
        if jump_block(s, '['):
            t = jump_block(s, '[')
            name = s[:t]
            list = []
            s = s[t + 1:]
            while 1:
                next = jump_block(s)
                list.append(s[:next])
                s = s[next + 1:]
                if (s):
                    s = s[1:]
                else:
                    break
            # print("Array:\n" + name + "\nList:")
            # l = len(list)
            # for i in range(l):
            #     print(list[i])
            ans = [name, list]
            return ans
        elif re.match("^" + NUMBER_REGEX + "$", s):
            # print("Number!")
            a = 0
        else:
            name = s
            ans = [name]
            # print("Var:\n" + name)
            return ans

    def parse_clear(self, s):
        l = len(s)
        ans = ""
        for i in range(l):
            if re.match('^' + INTERVAL_REGEX + '$', s[i:i + 1]):
                ans += ""
            else:
                ans += s[i]
        return ans

    def check_fun(self, s, list):
        l = len(list)
        for i in range(l):
            if s.find(list[i] + "(") == 0:
                return len(list[i])
        return 0

    def match(self, list, s):
        li = len(list)
        le = len(s)
        while le >= 0:
            for i in range(li):
                if re.match('^' + list[i] + '$', s[:le]):
                    return le
            le -= 1
        return -1

    def addMdf(self, ans):
        if (ans):
            if len(ans) == 2:
                self.Array_Mdf.append(ans)
            elif len(ans) == 1:
                self.Var_Mdf.append(ans[0])
                # else:
                #     #print("Error!")

    def addRdc(self, ans):
        self.Var_Rdc.append(ans)

    def addUse(self, ans):
        if ans:
            if len(ans) == 2:
                self.Array_Use.append(ans)
            elif len(ans) == 1:
                self.Var_Use.append(ans[0])
                # else:
                #     #print("Error!\n")

    def dfs(self, s, fa):
        if len(s) == 0:
            return
        if s[0] == '-':
            s = "0" + s
        # print(s)
        list = [["max", "min", "fmax", "fmin", "fabs", "abs"], ["(", ")"], ["!"], ["*", "/", "%"], ["+", "-"],
                ["<<", ">>"],
                [">=", "<=", ">", "<"], ["==", "!="], ["&"], ["^"], ["|"], ["&&"], ["||"]]
        li = len(list)
        # pos = []
        seg = []
        op = []
        while 1:
            # print(s)
            if s[0] == '(':
                t = jump_block(s[1:]) + 1
                seg.append(s[:t + 1])
                s = s[t + 1:]
            elif self.check_fun(s, list[0]):
                t = jump_block(s, "(")
                t = jump_block(s[t + 1:]) + t + 1
                seg.append(s[:t + 1])
                s = s[t + 1:]
            else:
                t = self.match([NAME_REGEX, NUMBER_REGEX], s)
                # print(t)
                while (t < len(s)) and (s[t] == '['):
                    t += 1
                    t = jump_block(s[t:]) + t
                    t += 1
                seg.append(s[:t])
                s = s[t:]
            if s:
                t = 2
                if (s[1] == '(') or (self.match([NAME_REGEX, NUMBER_REGEX], s[1:]) >= 0):
                    t -= 1
                op.append(s[:t])
                s = s[t:]
                # print(s)
            else:
                break

        l = len(seg)
        # for i in range(l):
        #     print(seg[i])
        # for i in range(l - 1):
        #     print(op[i])
        if len(seg) == 1:
            s = seg[0]
            if s[0] == '(':
                self.dfs(s[1:-1], fa)
            elif self.check_fun(s, list[0]):
                t = self.check_fun(s, list[0]) + 1
                op = s[:t - 1]
                # print(s[:t - 1])
                s = s[t:]
                t = jump_block(s, ',')
                left = s[:t]
                right = s[t + 1:-1]
                self.dfs(left, [op, 0])
                self.dfs(right, [op, 1])
            else:
                ans = self.parse_var(s)
                self.addUse(ans)
                self.var.append(ans)
                self.fa.append(fa)
                # print(s)
        else:
            i = li - 1
            while i > 0:
                k = len(list[i])
                # pos.append([])
                Max = -inf
                for j in range(k):
                    for id in range(l - 1):
                        if op[id] == list[i][j]:
                            Max = max(Max, id)
                if Max != -inf:
                    # print(op[Max])
                    left = right = ""
                    for tmp in range(Max + 1):
                        left += seg[tmp]
                        if tmp < Max:
                            left += op[tmp]
                    tmp = Max
                    while tmp < l - 1:
                        if (tmp > Max):
                            right += op[tmp]
                        right += seg[tmp + 1]
                        tmp += 1
                    self.dfs(left, [op[Max], 0])
                    self.dfs(right, [op[Max], 1])
                    break
                i = i - 1

    def checkRdc(self, check):
        l = len(self.var)
        cnt = 0
        fa = []
        # print(check)
        # for i in range(l):
        #     print(self.var[i]," ",self.fa[i])
        for i in range(l):
            if (self.var[i]) and (self.var[i][0] == check):
                cnt += 1
                if cnt > 1:
                    return None
                fa = self.fa[i]
        if cnt == 0:
            return None
        # print(fa)
        if (fa[0] in "+ * max fmax min fmin abs fabs & | && || ^") or ((fa[0] in "- / % << >>") and (fa[1] == 0)):
            return fa[0]
        return None

    def parse(self):
        if self.s == "":
            return
        s = self.s
        # print("====parse====\n" + s)
        s = self.parse_clear(s)
        # s=s[:-1]
        t = jump_block(s, '=')
        isProc = 0
        if t:
            flag = 0
            if ((s[t + 1] != '=') and (s[t - 1] != '!')) or (s[t - 2:t - 1] in ">>") or (s[t - 2:t - 1] in "<<"):
                isProc = 1
                while s[t - flag - 1] in "+-*/&|^<>%":
                    flag += 1
                ans = self.parse_var(s[:t - flag])
                self.addMdf(ans)
                op = s[t - flag:t]
                s = s[t + 1:]
                if flag > 0:
                    s = ans[0] + op + "(" + s + ")"
                self.dfs(s, ["", 0])
                if len(ans) == 1:
                    op = self.checkRdc(ans[0])
                    if op:
                        self.addRdc([ans[0], op])
        if not isProc:
            if ("++" in s) or ("--" in s):
                if s[0] in '+-':
                    ans = self.parse_var(s[2:])
                else:
                    ans = self.parse_var(s[:-2])
                if "++" in s:
                    op = "++"
                else:
                    op = "--"
                self.addMdf(ans)
                self.addUse(ans)
                if len(ans) == 1:
                    self.addRdc([ans[0], op])
            else:
                self.dfs(s, ["", 0])

    def merge(self, other):
        if other is None:
            return
        if other.interrupt:
            self.interrupt=True
        self.Array_Mdf = self.Array_Mdf + other.Array_Mdf
        self.Array_Use = self.Array_Use + other.Array_Use
        self.Var_Mdf = self.Var_Mdf + other.Var_Mdf
        self.Var_Use = self.Var_Use + other.Var_Use
        self.Var_Rdc = self.Var_Rdc + other.Var_Rdc


class Live:
    def __init__(self):
        self.live = []

    def kill(self, list):
        for i in range(len(list)):
            if list[i] in self.live:
                self.live.remove(list[i])

    def gen(self, list):
        for i in range(len(list)):
            if not (list[i] in self.live):
                self.live.append(list[i])

    def isUpdate(self, pre):
        if len(pre) != len(self.live):
            return True
        for i in range(len(pre)):
            if not (pre[i] in self.live):
                return True
        return False
