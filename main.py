#! /usr/bin/env python
# -*- coding: utf-8 -*-
# $Id:  $
# $Author:  $
from locale import setlocale, LC_NUMERIC
from ply import lex
from ply import yacc

# no funky stuff with strange number formatting please
setlocale(LC_NUMERIC, 'C')

# binnen een modal group kan er maar 1 actief zijn
# dus als G1 actief is kan G0 dat niet zijn
# modals hoeven niet iedere regel herhaald te worden

modal_G_groups = {
    'group1': (0,  # G0=rapid position
               1,  # G1=lineair motion
               2,  # G2=clockwise circle
               3,  # G3=counter clock wise
               80,  # G80 turns off all motion
               81, 82, 83,  # drill cycle
               84,  # tap cycle CW
               85,  # boring or reaming
               86,  # boring cycle
               87,  # back boring cycle
               88,  # boring cycle
               89  # boring cycle
               ),  # canned drill cycles
    'group2': (17,  # XY
               18,  # XZ
               19  # YZ
               ),  # plane selection G17=xy  G18=xz G19=yz
    'group3': (90,  # absolute distance mode
               91  # incremental distance mode
               ),  # distance mode
    'group5': (93,  # inverse time feed mode
               94  # feed per minute mode
               ),  # spindle speed mode
    'group6': (20, 21),  # units G20=inch G21=metric
    'group7': (40,  # Cancel Cutter compensation
               41,  # Cutter Compensation, Tool Left of Path
               42  # Cutter Compensation, Tool Right of Path
               ),  # Cutter Compensation

    'group8': (43,  # use tool offset H nnn
               49  # disable tool offset
               ),  # tool length offset

    'group10': (98,  # initial level return in cycles
                99  # R level return in cycles
                ),  # return mode in canned cycles

    'group12': (54, 55, 56, 57, 58, 59, 59.1, 59.2, 59.3)  # coordinate system selection
}

modal_M_groups = {
    'group2': (26,  # enable automatic B axis clamping
               27  # disable automatic B axis clamping
               ),  # axis clamping M26 M27

    'group4': (0,  # program stop
               1,  # optional program stop
               2,  # program end
               30,  # program end pallet shuttle and reset
               60  # pallet shuttle and program stop
               ),  # stopping

    'group6': (6,),  # tool change M6

    'group7': (3,  # clockwise spindle direction
               4,  # CCW spindle direction
               5  # spindle stop
               ),  # spindle turning

    'group8': (7,  # mist coolant on
               8,  # flood coolant on
               9  # mist and flood coolant OFF
               ),  # coolant

    'group9': (48,  # enable speed feed override
               49  # disable speed/feed override
               ),  # feed and speed override bypass
}

# global number to group G code translation table
# keys are strings
code_to_group = dict()

active_in_group = dict()  # global state about active G code
global_axis_value = dict()  # global state of Axis values X Y Z etc


class myLexer(object):
    tokens = ('EOL',  # end of line is einde block
              'PERCENT',  # start en eind van CNC programma
              'STAR',  # a '*' char
              'COLON',  # a ';' char
              'LINENUMBER',  # a 'N' with number
              'NUMBER',  # decimaal nummer met punt erin
              'COMMENTSTART', 'BODY', 'COMMENTEND',
              'WORD',  # letter M G X Y Z etc etc
              'BODY2',  # body van comment ';' met EOL
              'BODY3',  # body van comment M117 met EOL
              'COMMENT2END',  # token van comment EOL einde
              'COMMENT3END',  # token van comment EOL einde
              'M117',  # een comment met M117 start
              )

    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # NUMBER literal
    t_NUMBER = r'[-+]?\d+(\.\d+)?'
    t_EOL = r'\n'  # end of block
    t_PERCENT = '%'  # start end program
    t_STAR = r'\*'  # start a checksum value

    # An exclusive start-condition is where no other patterns are applied,
    # except those with the appropriate start-condition.

    # An inclusive start-condition is where the rule is applied
    # together will any other rules which are not constrained by start-conditions.
    states = (('comment', 'inclusive'),  # tussen haakjes ( comment )
              ('comment2', 'inclusive'),  # ';' comment
              ('comment3', 'inclusive'),  # een M117 comment tot EOL
              )

    def __init__(self):
        # constructor
        # lex.lex()
        self.lexer = None  # to keep pycharm happy

    def reset_lineno(self):
        """ Resets the internal line number counter of the lexer.
        """
        self.lexer.lineno = 1

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        g = self.lexer.token()
        return g

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)

    def t_COMMENTSTART(self, t):
        r'\('
        # start of comment chars
        t.lexer.push_state('comment')  # state wordt 'comments' conditioneel parsen dus!
        return t

    def t_comment_BODY(self, t):
        r'[^\)]+'
        # anything ignored inside comment
        # de tekst wordt teruggegeven omdat LinuxCNC hier commando's in zet, die je moet/kan parsen
        return t

    def t_comment_END(self, t):
        r'\)'
        # comment end with ) or end of block
        t.lexer.pop_state()
        t.type = 'COMMENTEND'
        return t

    def t_COLON(self, t):
        r';'
        # comment start ';' char
        t.lexer.push_state('comment2')  # parse tot EOL
        return t

    def t_comment2_BODY2(self, t):
        r'[^\n]+'
        # anything ignored inside comment2 state
        return t

    def t_comment2_EOL(self, t):
        r'[\n]'
        t.lexer.pop_state()
        t.type = 'COMMENT2END'  # return this instead of EOL
        return t

    def t_comment3(self, t):
        r'[mM]117'
        t.lexer.push_state('comment3')
        t.type = 'M117'
        return t

    def t_comment3_BODY3(self, t):
        r'[^\n]+'
        # anything ignored inside comment3 state
        return t

    def t_comment3_EOL(self, t):
        r'[\n]'
        t.lexer.pop_state()
        t.type = 'COMMENT3END'  # return this instead of EOL
        return t

    def t_WORD(self, t):
        r'(?i)[ABCUVWEFGHIJKLMPQRSTUVWXYZO]'
        return t

    def t_LINENUMBER(self, t):
        r'(?i)([Nn]\d+)'
        return t


class myParser(object):
    # There are a number of limitations about the number or types of words that can be strung together into a block.
    # The interpreter uses the following rules:
    #
    # A line may have zero to four G words.
    # Two G words from the same modal group may not appear on the same line.
    # A line may have zero to four M words.
    # Two M words from the same modal group may not appear on the same line.
    # For all other legal letters, a line may have only one word beginning with that letter.

    # start in rule
    start = 'program'

    def build(self, **kwargs):
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, **kwargs)
        self.execute_block = False
        self.execute_axis = set()
        self.groups_seen = set()

    def setlexer(self, lexer):
        self.lexer = lexer

    def test(self, data, debug=0):
        self.parser.parse(input=data, lexer=self.lexer, debug=debug)  # DEBUG FLAG

    def p_error(self, p):
        if p:
            print("Syntax error at token", p.type)
        # Just discard the token and tell the parser it's okay.
        self.parser.errok()

    def p_empty(self, p):
        """empty : """
        print(">empty")

    def p_program(self, p):
        """program :  opt_blocks
                   | PERCENT opt_blocks
        """

        print('programma klaar')

    def p_opt_blocks(self, p):
        """opt_blocks : empty
                      | blocks
        """

        print('blocks klaar')

    def p_blocks(self, p):
        """blocks : block
                  | blocks block
        """

        # print('handle block {b}'.format(b=p))

    def p_block(self, p):
        """block : opt_words EOL
                 | opt_words comment EOL
                 | comment EOL
                 | opt_words commenteol
                 | commenteol
                 | EOL
                 | LINENUMBER opt_words EOL
                 | LINENUMBER opt_words comment EOL
                 | LINENUMBER comment EOL
                 | LINENUMBER opt_words commenteol
                 | LINENUMBER commenteol
                 | LINENUMBER EOL
                 """
        if p[1] != '\n':
            print('Process the block now')

            self.groups_seen = set()  # reset groups seen in block

            if self.execute_block:
                print(global_axis_value)
                # group1 is movement
                print('group1 = g{g} movement'.format(g=active_in_group['group1']))
                # group6 is units
                print('group6 = g{g} units'.format(g=active_in_group['group6']))
                # changing axis
                print("moving axis {a}".format(a=self.execute_axis))
                self.execute_block = False
                self.execute_axis = set()  # empty

    def p_comment(self, p):
        """comment : COMMENTSTART COMMENTEND
                   | COMMENTSTART BODY COMMENTEND
        """
        print('handle comment : {c}'.format(c=p[2]))
        pass

    def p_commenteol(self, p):
        """commenteol : COLON COMMENT2END
                      | COLON BODY2 COMMENT2END"""

        print('handle comment : {c}'.format(c=p[2]))
        pass

    def p_comment3eol(self, p):
        """commenteol : M117 COMMENT3END
                      | M117 BODY3 COMMENT3END"""

        print('handle comment m117 : {c}'.format(c=p[2]))
        pass

    def p_opt_words(self, p):
        """opt_words : empty
                     | words
        """

    def p_words(self, p):
        """words : word
                 | words word
        """

        # print('nog een commando')

    def p_word(self, p):
        """word : WORD NUMBER"""

        print(p[1], p[2])
        # eerst de M en G codes eens bekijken
        # kunnen m g en M G zijn

        word = p[1].upper()  # nu dus M en G

        # G04 is gelijk aan G4 dus voorloop nullen eraf...
        # G059.1 is ook mogelijk dus int() valt af

        number = p[2].lstrip('0')  # strip leading zeroes
        # als het G00 was is number nu '' leeg niet handig
        if number == '':
            number = '0'

        if word == 'G':
            print('handle g code {x}'.format(x=number))
            # zoek de modal group for code
            group = code_to_group.get(number)
            if not group:
                # G code is not in global group, so local to this block eg G04
                print("warn, gcode not in any global group {x}".format(x=number))
            else:
                print("global g code {x} is in group {y}".format(x=number, y=group))
                active_in_group[group] = number
                # if group already seen in this block we have bad gcode
                if group in self.groups_seen:
                    print("Warning, illegal gcode, can not have multiple G codes from same group in single block")

                # group seen in this block, add to set
                self.groups_seen.add(group)

        if word == 'M':
            print('handle M code {x}'.format(x=number))
            # print('command {c} {x} type={t} value={v}'.format(c=word,x=number,t=p[1].type,v=p[1].value))

        if word in ('X', 'Y', 'Z',  # 3 axis
                    'A', 'B', 'C',  # 3 other axis
                    'U', 'V', 'W',  # 3 other axis
                    'E'  # extruder axis
                    ):
            # we have an axis, so block should do move something
            global_axis_value[word] = number
            self.execute_block = True

            if word in self.execute_axis:
                print("Warning, illegal gcode, can not have same axis multiple times in a block")

            self.execute_axis.add(word)  # deze axis is veranderd in deze block


if __name__ == '__main__':

    # convert modal groups for lookups

    for k in modal_G_groups:
        print(k)
        codes = modal_G_groups[k]
        for kk in codes:
            print(kk)
            code_to_group[str(kk)] = str(k)

    # set defaults for G code groups
    # default G codes
    default_gcode_at_start = 'G0 G17 G90 G94 G21 G40 G49 G54'
    for g in default_gcode_at_start.split():
        n = g[1:]
        active_in_group[code_to_group[n]] = n

    default_mcode_at_start = ''

    files = ('test_data/laser_output.nc', 'test_data/test_data1.nc',)

    m = myLexer()
    m.build()
    p = myParser()
    p.setlexer(m)
    p.build()

    for fn in files:
        print(">> Opening {i}".format(i=fn))
        # for i in loglines(open(name=fn).read()):  # or script
        with open(fn) as fx:
            hele_file = fx.read()
            p.parser.parse(hele_file)
