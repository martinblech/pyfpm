# pyfpm

`pyfpm` stands for PYthon Functional Pattern Matching. It's been heavily
inspired by the Pattern Matching and Case Classes implementation in Scala.

Build status at [Travis CI](http://travis-ci.org/): [![Build Status](https://secure.travis-ci.org/martinblech/pyfpm.png)](http://travis-ci.org/martinblech/pyfpm)

## Usage

With `pyfpm` you can unpack objects using the `Unpacker` class:

```python
unpacker = Unpacker()
unpacker('head :: tail') << (1, 2, 3)
unpacker.head # 1
unpacker.tail # (2, 3)
```

or function parameters using the `match_args` decorator:

```python
@match_args('[x:str, [y:int, z:int]]')
def match(x, y, z):
    return (x, y, z)

match('abc', (1, 2)) # ('abc', 1, 2)
```

You can also create simple matchers with lambda expressions using the `Matcher`
class:

```python
what_is_it = Matcher([
    ('_:int', lambda: 'an int'),
    ('_:str', lambda: 'a string'),
    ('x', lambda x: 'something else: %s' % x),
    ])

what_is_it(10)    # 'an int'
what_is_it('abc') # 'a string'
what_is_it({})    # 'something else: {}'
```

or more complex ones using the `Matcher.handler` decorator:

```python
parse_options = Matcher()
@parse_options.handler("['-h'|'--help', None]")
def help():
    return 'help'
@parse_options.handler("['-o'|'--optim', level:int] if 1<=level<=5")
def set_optimization(level):
    return 'optimization level set to %d' % level
@parse_options.handler("['-o'|'--optim', bad_level]")
def bad_optimization(bad_level):
    return 'bad optimization level: %s' % bad_level
@parse_options.handler('x')
def unknown_options(x):
    return 'unknown options: %s' % repr(x)

parse_options(('-h', None))     # 'help'
parse_options(('--help', None)) # 'help'
parse_options(('-o', 3))        # 'optimization level set to 3'
parse_options(('-o', 0))        # 'bad optimization level: 0'
parse_options(('-v', 'x'))      # "unknown options: ('-v', 'x')"
```

For more information, see the files in the `examples` directory alongside the
links within them, or [read the docs](http://pyfpm.readthedocs.org/).
