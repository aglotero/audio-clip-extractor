# -*- coding: utf-8 -*-
import os
import zipfile
import subprocess

from pkg_resources import resource_filename, Requirement

from .parser import LabelsParser, AudioClipSpec

# import tbutils  # My utils library

class AudioClipCutter(object):
    def __init__(self, audioFilePath, ffmpegPath):
        self._audioFilePath = audioFilePath
        self._ffmpegPath = ffmpegPath
        self._audioFileData = None
        self._textVar = 'm_text'

    @property
    def textVar(self):
        return self._textVar

    @textVar.setter
    def textVar(self, value):
        self._textVar = value

    def extractClips(self, specsFilePathOrData, outputDir=None, zipOutput=False):
        parser = LabelsParser(specsFilePathOrData)
        clips = parser.parseClips()

        # Output to current working directory if no outputDir was provided
        if not outputDir:
            outputDir = os.path.abspath('.')

        zipFile = None
        if zipOutput:
            bname = os.path.splitext(os.path.basename(specsFilePathOrData))[0]
            zipPath = "%s_clips.zip" % bname
            zipFile = zipfile.ZipFile(os.path.join(outputDir, zipPath), mode='w')

        for i, clip in enumerate(clips):
            # 13 clips => clip01.mp3, clip12.mp3...
            filenameFormat = 'clip%%0%dd.mp3' % len(str(len(clips)))

            filepath = os.path.join(outputDir, filenameFormat % (i+1))

            clipData = self._extractClipData(clip)

            with open(filepath, 'wb') as f_out:
                f_out.write(clipData)

            if zipFile:
                zipFile.write(filepath, arcname=os.path.basename(filepath))
                os.unlink(filepath)

        if zipFile:
            zipFile.close()

    def _extractClipData(self, audioClipSpec, showLogs=False):
        command = [self._ffmpegPath]

        if not showLogs:
            command += ['-nostats', '-loglevel', '0']

        command += [
            '-i', self._audioFilePath,
            '-ss', '%.3f' % audioClipSpec.start,
            '-t', '%.3f' % audioClipSpec.duration(),
            '-c', 'copy',
            '-map', '0',
            '-acodec', 'libmp3lame',
            '-ab', '128k',
            '-f', 'mp3'
        ]

        # Add clip TEXT as metadata and set a few more to default
        metadata = {self._textVar: audioClipSpec.text}
            # title='Extracted clip',
            # album='N/A',
            # genre='Shadowing',
            # artist='N/A')

        for k, v in metadata.items():
            command.append('-metadata')
            command.append("{}='{}'".format(k, v))

        command.append('pipe:1')

        return subprocess.check_output(command)

    def _readFileData(self, filePathOrData):
        data = None
        try:
            none = self.filePathOrData.read()
        except Exception as e:
            pass

        if not data:
            try:
                with open(filePathOrData, 'rb') as f:
                    data = f.read()
            except Exception as e:
                raise

        return data
