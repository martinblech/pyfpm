import re
import inspect

from pyparsing import Literal, Word, Group, Combine, Suppress,\
        Forward, Optional, alphas, nums, alphanums, QuotedString,\
        quotedString, dblQuotedString, removeQuotes, delimitedList,\
        ParseException, Keyword, restOfLine, ParseFatalException

from pyfpm.pattern import build as _

def _get_caller_globals():
    frame = inspect.getouterframes(inspect.currentframe())[2][0]
    return frame.f_globals

class IfCondition(object):
    def __init__(self, code, context):
        self.code = code
        self.context = context

    def __call__(self, **kwargs):
        return eval(self.code, self.context, kwargs)

    def __eq__(self, other):
        return (isinstance(other, IfCondition) and
                self.__dict__ == other.__dict__)
    
    def __str__(self):
        return 'IfCondition(code=%s, context=%s)' % (
                self.code,
                self.context)

def Parser(context=None):
    if context is None:
        context = _get_caller_globals()

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
            lambda *args: get_type(args[-1].type_))

    anon_var = Literal("_")('anon_var').setParseAction(lambda *args: _())

    named_var = Word(alphas, alphanums + '_')('named_var').setParseAction(
            lambda *args: get_named_var(args[-1].named_var))

    untyped_var = (named_var | anon_var)('untyped_var')

    typed_var = (untyped_var + Suppress(':') + type_)(
            'typed_var').setParseAction(
            lambda *args: _(args[-1].type_)%args[-1].untyped_var.bound_name)

    var = (typed_var | untyped_var)('var')

    int_const = Combine(Optional('-') + Word(nums))(
            'int_const').setParseAction(lambda *args: int(args[-1].int_const))

    float_const = Combine(Optional('-') + Word(nums) + Literal('.')
            + Optional(Word(nums)) |
            Optional('-') + Literal('.') + Word(nums))(
            'float_const').setParseAction(
                    lambda *args: float(args[-1].float_const))

    str_const = (quotedString | dblQuotedString)('str_const').setParseAction(
            removeQuotes)

    regex_const = QuotedString(quoteChar='/', escChar='\\')('regex_const'
            ).setParseAction(lambda *args: re.compile(args[-1].regex_const))

    true = Keyword('True').setParseAction(lambda *args: _(True))
    false = Keyword('False').setParseAction(lambda *args: _(False))
    null = Keyword('None').setParseAction(lambda *args: _(None))

    const = (float_const | int_const | str_const | regex_const |
            false | true | null)('const').setParseAction(
                    lambda *args: _(args[-1].const))

    scalar = Forward()

    pattern = Forward()

    head_tail = (scalar + Suppress('::') + pattern)(
            'head_tail').setParseAction(lambda *args: args[-1][0] + args[-1][1])

    list_item = (pattern | scalar)('list_item')

    list_contents = Optional(delimitedList(list_item))('list_contents')

    full_list = (Suppress('[') + list_contents + Suppress(']'))(
            'full_list').setParseAction(lambda *args: _(list(args[-1])))

    list_ = (head_tail | full_list)('list')

    case_class = Combine(type_ + Suppress('(') + list_contents +
            Suppress(')'))('case_class').setParseAction(
                lambda *args: _(args[-1][0].type_(*args[-1][0].list_contents)))

    scalar << (const | var | case_class |
            Suppress('(') + pattern + Suppress(')'))('scalar')

    or_clause = (list_ | scalar)('or_clause')

    or_expression = (or_clause + Suppress('|') + pattern)(
            'or_expression').setParseAction(
                    lambda *args: args[-1][0] | args[-1][1])

    def conditional_pattern_action(*args):
        try:
            pattern, condition_string = args[-1]
            code = compile(condition_string.strip(),
                    '<pattern_condition>', 'eval')
            pattern.if_(IfCondition(code, context))
            return pattern
        except ValueError:
            pass

    pattern << ((or_expression | or_clause) +
            Optional(Suppress(Keyword('if')) + restOfLine))(
                    'pattern').setParseAction(conditional_pattern_action)

    # end grammar

    def parse(expression):
        (p,) = pattern.parseString(expression, parseAll=True)
        return p

    parse.context = context
    parse.setDebug = pattern.setDebug
    return parse
