"""

for zyh:

you just import cparser
and then use:
car, cdr, cparser, generator, unique_generator
from cparser




not support:

(type){list}
{list}
#define
typedef
sizeof x
.
*
->
&
pointer operators
pointer array
struct
immediate initialization
static
switch
default parameter
exit(?)
do{}while()


but support:
list??

"""

from regex import *
from expr import Expr, Live


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


class Program:
    def __renew(self):
        if self.text:
            match = re.match(ESSENTIAL_REGEX, self.text)
            if match:
                dlt = match.span()[1] - 1
                if dlt:
                    self.text = self.text[dlt:]
                    self.cur += dlt
            else:
                self.cur += len(self.text)
                self.text = None

    def __init__(self, text=None, cur=None):
        self.text = text
        self.cur = cur
        self.dlt = None
        self.__renew()

    def front_match(self, reg):
        match = re.match(reg, self.text) if self.text else None
        self.dlt = match.span()[1] if match else None
        return self.dlt

    def front_jump(self, ex=''):
        self.dlt = jump_block(self.text, ex)
        return self.dlt

    def erase(self, l):
        self.text = self.text[l:]
        self.cur += l
        self.__renew()

    def forward(self, l=0):
        if self.dlt is not None:
            l += self.dlt
            self.dlt = None
            self.erase(l)

    def group(self, l=0):
        if self.dlt is not None:
            return self.text[:self.dlt + l]

    def __str__(self):
        return self.text

    def __bool__(self):
        return True if self.text else False

    def __getitem__(self, item):
        if self:
            dlt = 0
            if item.start:
                dlt = item.start
                if dlt < 0:
                    dlt += len(self.text)
            text = self.text[item]
            return Program(text, self.cur + dlt)
        return None


def add_edge(a_inst, b_inst):
    a_inst.succ_inst.append(b_inst)
    b_inst.pred_inst.append(a_inst)


class Instruction:
    instruction_count = 0
    program_text = ''

    def __init__(self, pc=None, expression=None, env=None):
        self.succ_inst = []
        self.pred_inst = []
        self.category = None
        self.jump = None
        self.isLikely = False
        self.live = Live()
        self.son = []
        if pc:
            add_edge(pc, self)
        self.expression = Expr(expression) if expression else Expr("")
        self.env = env
        self.line = None
        self.node_id = Instruction.instruction_count
        Instruction.instruction_count += 1

    def set_line(self, cur):
        self.line = count(Instruction.program_text[:cur], '\n') + 1

    def __str__(self):
        return str(self.expression)


"""
car : values
cdr : arrays
"""

if_struct = 'if'
for_struct = 'for'
while_struct = 'while'
main_struct = 'main'


def car(table):
    return table[0]


def cdr(table):
    return table[1]


def generator(env):
    while env:
        yield car(env)
        env = cdr(env)


def unique_generator(env):
    vals, arrs = set([]), set([])
    for (values, arrays) in generator(env):
        yield ([value for value in values if value not in vals],
               [array for array, _ in arrays if array not in arrs])
        for value in values:
            vals.add(value)
        for array, _ in arrays:
            arrs.add(array)


def parse_vars_def(arg, program):
    (values, arrays) = arg
    while program:
        word = None
        while program.front_match(NAME_HEADER_REGEX):
            word = program.group(-1)
            program.forward(-1)
        level = 0
        while program.text[0] == '[':
            program.erase(jump_block(program.text[1:]) + 2)
            level += 1
        program.erase(1)
        if level:
            arrays.append((word, level))
        else:
            values.append(word)


class Graph:
    def parse_block(self, program, pc, env, ctn_inst, brk_inst, ret_inst):
        dlt = 1 + jump_block(program.text[1:])
        pc = self.parse_lines(program[1:dlt], pc, (([], []), env), ctn_inst, brk_inst, ret_inst)
        program.erase(dlt + 1)
        return pc

    def parse_statement(self, program, pc, env, ctn_inst, brk_inst, ret_inst):
        if program.text[0] == '{':
            pc = self.parse_block(program, pc, env, ctn_inst, brk_inst, ret_inst)
        else:
            program.front_jump(';')
            pc = self.parse_lines(program[:program.dlt + 1], pc, (([], []), env), ctn_inst, brk_inst, ret_inst)
            program.forward(1)
        return pc

    def parse_lines(self, program, pc, env, ctn_inst, brk_inst, ret_inst):
        while program:
            if program.text[0] == '{':
                # block
                pc = self.parse_block(program, pc, env, ctn_inst, brk_inst, ret_inst)

            elif program.front_match(IF_HEADER_REGEX):
                # if (expr) [expr; | block] [else [expr; | block]]?
                program.forward()
                program.front_jump()
                pc = Instruction(pc=pc, expression=program.group(), env=env)
                program.forward(1)

                end = Instruction(pc=self.parse_statement(program, pc, env, ctn_inst, brk_inst, ret_inst), env=env)
                pc.jump = end
                pc.category = if_struct

                if program.front_match(ELSE_HEADER_REGEX):
                    program.forward(-1)
                    add_edge(self.parse_statement(program, pc, env, ctn_inst, brk_inst, ret_inst), end)

                else:
                    add_edge(pc, end)

                pc = end

            elif program.front_match(FOR_HEADER_REGEX):
                # for ( pc; pc; renew) [expr; | block]
                program.forward()
                program.front_jump(';')
                pc = Instruction(pc=pc, expression=program.group(), env=env)
                begin = pc
                begin.category = for_struct
                begin.set_line(program.cur)
                program.forward(1)
                program.front_jump(';')
                pc = Instruction(pc=pc, expression=program.group(), env=env)
                program.forward(1)
                program.front_jump()
                renew = Instruction(expression=program.group(), env=env)
                program.forward(1)
                add_edge(renew, pc)
                end = Instruction(pc=pc, env=env)
                add_edge(self.parse_statement(program, pc, env, renew, end, ret_inst), renew)
                begin.jump = end
                pc = end

            elif program.front_match(WHILE_HEADER_REGEX):
                # while (expr) [expr; | block]
                program.forward()
                program.front_jump()
                pc = Instruction(pc=pc, expression=program.group(), env=env)
                program.forward(1)
                end = Instruction(pc=pc, env=env)
                pc.category = while_struct
                pc.jump = end
                add_edge(self.parse_statement(program, pc, env, pc, end, ret_inst), pc)
                pc = end

            elif program.front_match(BREAK_REGEX):
                # break;
                program.forward()
                add_edge(pc, brk_inst)
                return pc

            elif program.front_match(CONTINUE_REGEX):
                # continue;
                program.forward()
                add_edge(pc, ctn_inst)
                return pc

            elif program.front_match(RETURN_REGEX):
                # return ?;
                program.forward(-1)
                program.front_jump(';')
                program.forward(1)
                add_edge(pc, ret_inst)
                return pc

            else:
                # [expr | vars_def];
                program.front_jump(';')
                if is_expression(program.group()):
                    pc = Instruction(pc=pc, expression=program.group(), env=env)
                else:
                    parse_vars_def(car(env), program[:program.dlt + 1])
                program.forward(1)

        return pc

    def __init__(self, program):

        global_vars = ([], [])
        self.begin = self.end = None

        while program:

            if program.front_match(INCLUDE_REGEX):
                program.forward()

            elif program.text[program.front_jump(';{')] == ';':
                # variables definition
                parse_vars_def(arg=global_vars, program=program[:program.dlt + 1])
                program.forward(1)

            else:
                if self.begin:
                    exit(-1)
                    # there is only one function

                env = (global_vars, None)
                program.forward()
                self.begin = Instruction(env=env)
                self.end = Instruction(env=env)

                self.begin.jump = self.end
                self.begin.category = main_struct

                pc = self.parse_block(program=program, pc=self.begin, env=env,
                                      ctn_inst=None, brk_inst=None, ret_inst=self.end)

                add_edge(pc, self.end)


def cparser(text):
    Instruction.instruction_count = 0
    Instruction.program_text = text
    return Graph(Program(text, 0))
