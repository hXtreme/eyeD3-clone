# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2016  Sebastian Patschorke <physicspatschi@gmx.de>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import sys
if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest
from nose.tools import *
from eyed3.plugins.display import *
from eyed3.id3 import TagFile


class TestDisplayPlugin(unittest.TestCase):

    def __init__(self, name):
        super(TestDisplayPlugin, self).__init__(name)

    def testSimpleTags(self):
        self.file.tag._setArtist(u"The Artist")
        self.file.tag._setTitle(u"Some Song")
        self.__checkOutput(u"%a% - %t%", u"The Artist - Some Song")

    def testRepeatFunction(self):
        self.__checkOutput(u"$repeat(*,3)", u"***")
        self.__checkException(u"$repeat(*,three)", DisplayException)

    def testNotEmptyFunction(self):
        self.__checkOutput(u"$not-empty(foo,hello #t,nothing)", u"hello foo")
        self.__checkOutput(u"$not-empty(,hello #t,nothing)", u"nothing")

    def testNumberFormatFunction(self):
        self.__checkOutput(u"$num(123,5)", u"00123")
        self.__checkOutput(u"$num(123,3)", u"123")
        self.__checkOutput(u"$num(123,0)", u"123")
        self.__checkException(u"$num(nan,1)", DisplayException)
        self.__checkException(u"$num(1,foo)", DisplayException)
        self.__checkException(u"$num(1,)", DisplayException)

    def __checkOutput(self, pattern, expected):
        output = Pattern(pattern).output_for(self.file)
        assert_equal(output, expected)

    def __checkException(self, pattern, exception_type):
        with assert_raises(exception_type):
            Pattern(pattern).output_for(self.file)

    def setUp(self):
        import tempfile
        with tempfile.NamedTemporaryFile() as temp:
            temp.flush()
            self.file = TagFile(temp.name)
        self.file.initTag()

    def tearDown(self):
        pass


class TestDisplayParser(unittest.TestCase):

    def __init__(self, name):
        super(TestDisplayParser, self).__init__(name)

    def testTextPattern(self):
        pattern = Pattern(u"hello")
        assert_is_instance(pattern.sub_patterns[0], TextPattern)
        assert_equal(len(pattern.sub_patterns), 1)

    def testTagPattern(self):
        pattern = Pattern(u"%comments,desc,lang,separation=|%")
        assert_equal(len(pattern.sub_patterns), 1)
        assert_is_instance(pattern.sub_patterns[0], TagPattern)
        comments_tag = pattern.sub_patterns[0]
        assert_equal(len(comments_tag.parameters), 4)
        assert_equal(comments_tag.parameter_value(u"description", None), u"desc")
        assert_equal(comments_tag.parameter_value(u"language", None), u"lang")
        assert_equal(comments_tag.parameter_value(u"output", None), AllCommentsTagPattern.PARAMETERS[2].default)
        assert_equal(comments_tag.parameter_value(u"separation", None), u"|")

    def testComplexPattern(self):
        pattern = Pattern(u"Output: $format(Artist: $not-empty(%artist%,#t,none),bold=y)")
        assert_equal(len(pattern.sub_patterns), 2)
        assert_is_instance(pattern.sub_patterns[0], TextPattern)
        assert_is_instance(pattern.sub_patterns[1], FunctionFormatPattern)
        text_patten = pattern.sub_patterns[1].parameters['text'].value
        assert_equal(len(text_patten.sub_patterns), 2)
        assert_is_instance(text_patten.sub_patterns[0], TextPattern)
        assert_is_instance(text_patten.sub_patterns[1], FunctionNotEmptyPattern)

    def testCompileException(self):
        with assert_raises(PatternCompileException):
            Pattern(u"$bad-pattern").output_for(None)
        with assert_raises(PatternCompileException):
            Pattern(u"$unknown-function()").output_for(None)

    def setUp(self):
        pass

    def tearDown(self):
        pass
