# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2009  Travis Shirk <travis@pobox.com>
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
from __future__ import print_function
import os
from eyed3 import LOCAL_ENCODING as ENCODING
from eyed3.utils import formatSize, formatTime
from eyed3.utils.cli import (printMsg, printError, printWarning, boldText,
                             getColor, RESET, HEADER_COLOR)
from eyed3.plugins import LoaderPlugin

class LameInfoPlugin(LoaderPlugin):
    NAMES = ["lameinfo", "xing"]
    SUMMARY = u"Outputs lame header (if one exists) for file."

    def printHeader(self, filePath):
        from stat import ST_SIZE
        fileSize = os.stat(filePath)[ST_SIZE]
        size_str = formatSize(fileSize).encode(ENCODING)
        print("\n%s\t%s[ %s ]%s" % (boldText(os.path.basename(filePath),
                                             HEADER_COLOR),
                                    getColor(HEADER_COLOR), size_str,
                                    getColor(RESET)))
        print("-" * 79)

    def handleFile(self, f):
        super(LameInfoPlugin, self).handleFile(f)

        self.printHeader(f)
        if not self.audio_file or not self.audio_file.info.lame_tag:
            printMsg('No LAME Tag')
            return self.R_CONT

        format = '%-20s: %s'
        lt = self.audio_file.info.lame_tag
        if not lt.has_key('infotag_crc'):
            try:
                printMsg('%s: %s' % ('Encoder Version', lt['encoder_version']))
            except KeyError:
                pass
            return self.R_CONT

        values = []

        values.append(('Encoder Version', lt['encoder_version']))
        values.append(('LAME Tag Revision', lt['tag_revision']))
        values.append(('VBR Method', lt['vbr_method']))
        values.append(('Lowpass Filter', lt['lowpass_filter']))

        if lt.has_key('replaygain'):
           try:
               peak = lt['replaygain']['peak_amplitude']
               db = 20 * math.log10(peak)
               val = '%.8f (%+.1f dB)' % (peak, db)
               values.append(('Peak Amplitude', val))
           except KeyError:
               pass
           for type in ['radio', 'audiofile']:
               try:
                   gain = lt['replaygain'][type]
                   name = '%s Replay Gain' % gain['name'].capitalize()
                   val = '%s dB (%s)' % (gain['adjustment'], gain['originator'])
                   values.append((name, val))
               except KeyError:
                   pass

        values.append(('Encoding Flags', ' '.join((lt['encoding_flags']))))
        if lt['nogap']:
            values.append(('No Gap', ' and '.join(lt['nogap'])))
        values.append(('ATH Type', lt['ath_type']))
        values.append(('Bitrate (%s)' % lt['bitrate'][1], lt['bitrate'][0]))
        values.append(('Encoder Delay', '%s samples' % lt['encoder_delay']))
        values.append(('Encoder Padding', '%s samples' % lt['encoder_padding']))
        values.append(('Noise Shaping', lt['noise_shaping']))
        values.append(('Stereo Mode', lt['stereo_mode']))
        values.append(('Unwise Settings', lt['unwise_settings']))
        values.append(('Sample Frequency', lt['sample_freq']))
        values.append(('MP3 Gain', '%s (%+.1f dB)' % (lt['mp3_gain'],
                                                      lt['mp3_gain'] * 1.5)))
        values.append(('Preset', lt['preset']))
        values.append(('Surround Info', lt['surround_info']))
        values.append(('Music Length', '%s' % formatSize(lt['music_length'])))
        values.append(('Music CRC-16', '%04X' % lt['music_crc']))
        values.append(('LAME Tag CRC-16', '%04X' % lt['infotag_crc']))

        for v in values:
            printMsg(format % (v))
