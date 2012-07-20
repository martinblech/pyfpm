from __future__ import print_function
import inspect

from pyparsing import Literal, Word, Group, Combine, Suppress, OneOrMore,\
        Forward, Optional, alphas, nums, alphanums, stringEnd, oneOf,\
        quotedString, dblQuotedString, removeQuotes, delimitedList,\
        ParseException

from pyfpm import build as _

def Parser(context=None):
    if context is None:
        frame = inspect.getouterframes(inspect.currentframe())[1][0]
        context = frame.f_globals

    # parsing actions
    def get_type(type_name):
        try:
            t = eval(type_name, context)
        except NameError:
            raise ParseException('unknown type: %s' % type_name)
        if not isinstance(t, type):
            raise ParseException('not a type: %s' % type_name)
        return t

    def get_named_var(var_name):
        try:
            get_type(var_name)
        except ParseException:
            return _()%var_name
        raise ParseException('var name clashes with type: %s' % var_name)

    # begin grammar
    type_ = Word(alphas, alphanums + '._')('type_').setParseAction(
            lambda r, *x: get_type(r.type_))

    anon_var = Literal("_")('anon_var').setParseAction(lambda *x: _())

    named_var = Word(alphas, alphanums + '_')('named_var').setParseAction(
            lambda r, *x: get_named_var(r.named_var))

    untyped_var = (named_var | anon_var)('untyped_var')

    typed_var = (untyped_var + Suppress(':') + type_)(
            'typed_var').setParseAction(
            lambda r, *x: _(r.type_)%r.untyped_var.bound_name)

    var = (typed_var | untyped_var)('var')

    int_const = Combine(Optional('-') + Word(nums))(
            'int_const').setParseAction(lambda r, *x: int(r.int_const))

    float_const = Combine(Optional('-') + Word(nums) + Literal('.')
            + Optional(Word(nums)) |
            Optional('-') + Literal('.') + Word(nums))(
            'float_const').setParseAction(lambda r, *x: float(r.float_const))

    str_const = (quotedString | dblQuotedString)('str_const').setParseAction(
            removeQuotes)

    const = (float_const | int_const | str_const)(
            'const').setParseAction(lambda r, *x: _(r.const))

    scalar = (var | const)('scalar')

    pattern = Forward()

    head_tail = (scalar + Suppress('::') + pattern)(
            'head_tail').setParseAction(lambda r, *x: r[0] + r[1])

    list_item = (scalar | pattern)('list_item')

    full_list = (Suppress('[') + Optional(delimitedList(list_item)) +
            Suppress(']'))('full_list').setParseAction(lambda r, *x: _(list(r)))

    list_ = (head_tail | full_list)('list')

    or_clause = (list_ | scalar)('or_clause')

    or_expression = (or_clause + Suppress('|') + pattern)(
            'or_expression').setParseAction(lambda r, *x: r[0] | r[1])

    pattern << (or_expression | or_clause)('pattern')
    # end grammar

    def parse(expression):
        return pattern.parseString(expression, parseAll=True)[0]

    parse.context = context
    return parse
