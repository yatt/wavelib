# coding: utf-8
import wave
import array
import sys
import os
import tempfile

class WaveInitializer(object):
    def initialize(self, waveobj):
        pass

class SinWaveInit(WaveInitializer):
    def __init__(self, freq):
        super(SinWaveInit, self).__init__()
    def initialize(self, wav):
        pass

class SquareWaveInit(WaveInitializer):
    # todo
    pass

class TriangleWaveInit(WaveInitializer):
    # todo
    pass



# effector
class AudioEffector(object):
    pass

class Delay(AudioEffector):
    pass

# todo: etc effector

class EffectorComposer(object):
    pass






class AudioFrame(object):
    def __init__(self, src, i):
        sefl.src = src
        self.i = i


CH_MONO = 1
CH_STEREO = 2
BITS_8 = 8
BITS_16 = 16
class WaveInfo(object):
    def __init__(self, ch, bits, freq, nframes):
        self.channel = ch
        self.bits = bits
        self.freq = freq
        self.nframes = nframes
    __slots__ = ['channel', 'bits', 'freq', 'nframes']


class Wave(object):
    def __init__(self, obj, initializer=None):
        self.info = None
        self.raw = None
        if isinstance(obj, WaveInfo):
            self._init(obj, initializer)
        else: # filepath
            self._read(obj)
    def _init(self, info, init):
        self.info = info
        if init:
            init.initialize(self)
    def _read(self, filepath):
        try:
            ifs = wave.open(filepath, 'rb')
            args = (
                ifs.getnchannels(),
                ifs.getsampwidth(),
                ifs.getframerate(),
                ifs.getnframes()
                )
            self.info = WaveInfo(*args)
            dtype = 'Bh'[ifs.getnchannels() - 1]
            frame = ifs.readframes(ifs.getnframes())
            self.raw = array.array(dtype, frame)
        except Exception, e:
            raise e
    def _write(self, filepath):
        try:
            ofs = wave.open(filepath, 'wb')
            ofs.setnchannels(self.info.channel)
            ofs.setsampwidth(self.info.bits)
            ofs.setframerate(self.info.freq)
            ofs.setnframes(self.info.nframes)
            ofs.writeframes(self.raw)
            ofs.close()
        except: # todo
            pass
    def saveas(self, filepath):
        self._write(filepath)

    def play(self):
        self.playsync()

    def playsync(self):
        # todo: create truely temporary file path
        from random import choice
        from string import letters
        filepath = ''.join(choice(letters) for _ in range((32)))

        try:
            self.saveas(filepath)
            self.playfilesync(filepath)
        finally:
            try:
                os.remove(filepath)
            except:
                pass
        
    def playfilesync(self, filepath):
        if sys.platform == 'linux2':
            import ossaudiodev
            wav = wave.open(filepath, 'r')
            dev = ossaudiodev.open('w')
            format = [None, ossaudiodev.AFMT_U8, ossaudiodev.AFMT_S16_LE][wav.getsampwidth()]
            dev.setparameters(format, wav.getnchannels(), wav.getframerate())
            dev.write(wav.readframes(wav.getnframes()))
        elif sys.platform == 'macosx':
            import AppKit
            sound = AppKit.NSSound.alloc()
            sound.initWithContentsOfFile_byReference_(filepath, True)
            sound.play()
            while sound.isPlaying():
                pass
        elif sys.platform == 'win32':
            import winsound
            winsound.PlaySound(filepath, winsound.SND_FILENAME)

    def playasync(self):
        raise NotImplementedError('')
    
    def __index__(self, i):
        pass

