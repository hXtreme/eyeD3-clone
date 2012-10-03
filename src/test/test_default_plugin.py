# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2012  Travis Shirk <travis@pobox.com>
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
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
################################################################################
from nose.tools import *
from eyed3 import main, info
from . import DATA_D, RedirectStdStreams

def testPluginOption():
    # When help is requested and no plugin is specified, use default
    for arg in ["--help", "-h"]:
        with RedirectStdStreams() as out:
            try:
                args, parser = main.parseCommandLine([arg])
            except SystemExit as ex:
                assert_equal(ex.code, 0)
                out.stdout.seek(0)
                sout = out.stdout.read()
                assert_not_equal(
                        sout.find("Plugin options:\n  Classic eyeD3"), -1)

    # When help is requested and all default plugin names are specified
    for plugin_name in ["default", "classic", "editor"]:
        for args in [["--plugin=%s" % plugin_name, "--help"]]:
            with RedirectStdStreams() as out:
                try:
                    args, parser = main.parseCommandLine(args)
                except SystemExit as ex:
                    assert_equal(ex.code, 0)
                    out.stdout.seek(0)
                    sout = out.stdout.read()
                    assert_not_equal(
                            sout.find("Plugin options:\n  Classic eyeD3"), -1)

