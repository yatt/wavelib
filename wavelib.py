# coding: utf-8
import wave
import array
import sys
import os
import tempfile


BITS_8 = 8
BITS_16 = 16
class WaveInfo(object):
    __slots__ = [
        'channel',
        'bits',
        'freq',
        'nframes',
        'maxvalue',
        'minvalue',
        ]
    def __init__(self, ch, bits, freq, nframes):
        self.channel = ch
        self.bits = bits
        self.freq = freq
        self.nframes = nframes
        self.maxvalue = [255, 32768][ch - 1]
        self.minvalue = [0, -32767][ch - 1]


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
        dtype = 'Bh'[info.channel- 1]
        datag = (0 for _ in xrange(info.nframes))
        self.raw = array.array(dtype, datag)
        if init:
            init.initialize(self)
    def _read(self, filepath):
        try:
            ifs = wave.open(filepath, 'rb')
            args = (
                ifs.getnchannels(),
                ifs.getsampwidth() * 8,
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
            ofs.setsampwidth(self.info.bits / 8)
            ofs.setframerate(self.info.freq)
            ofs.setnframes(self.info.nframes)
            ofs.writeframes(self.raw.tostring())

            ofs.close()
        except Exception, e: # todo
            raise e
    def saveas(self, filepath):
        self._write(filepath)

    def __getitem__(self, i):
        if self.info.channel == 1:
            return AudioFrameMonoral(self, i)
        else:
            return AudioFrameStereo(self, i)
    def __len__(self):
        return self.info.nframes
    def __iter__(self):
        for i in xrange(len(self)):
            yield self[i]

    def play(self):
        self.playsync()

    def _tempfile(self):
        from random import choice
        from string import letters
        filepath = ''.join(choice(letters) for _ in range((32)))
        # todo: create truely temporary file path
        if sys.platform == 'win32':
            path = os.path.join(os.environ['TEMP'], filepath)
        else:
            path = filepath
        return path

    def playsync(self):
        filepath = self._tempfile()
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
    




class WaveInitializer(object):
    def initialize(self, waveobj):
        pass

class SinWaveInit(WaveInitializer):
    def __init__(self, freq):
        super(SinWaveInit, self).__init__()
        self.freq = freq
    def initialize(self, wav):
        import math
        p2 = 2.0 * math.pi
        fi = wav.info.freq
        fs = self.freq
        for i,frame in enumerate(wav):
            p = p2 * float(i % fi) / fi
            v = math.sin(p * fs)
            frame.value = v

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
        self.src = src
        self.i = i

class AudioFrameMonoral(AudioFrame):
    def __init__(self, src, i):
        super(AudioFrameMonoral, self).__init__(src, i)
    def _setval(self, val): # -1.0 <= val <= +1.0
        val = int((val + 1) / (2.0 / 255))
        self.src.raw[self.i] = val
    def _getval(self):
        return self.src.raw[self.i]
    value = property(_getval, _setval)

class AudioFrameStereo(AudioFrame):
    def __init__(self, src, i2):
        super(AudioFrameStereo, self).__init__(sec, i2)
        print 'h'
    def _setleft(self, val):
        val = int((val + 1) / (2.0 / 32767))
        self.src.raw[self.i2] = val
    def _getleft(self):
        return self.src.raw[self.i2]
    def _setright(self, val):
        val = int((val + 1) / (2.0 / 32767))
        self.src.raw[self.i2 + 1] = val
    def _getright(self):
        return self.src.raw[self.i2]
    #def _setvalue(self, val):
    #    val = int((val + 1) / (2.0 / 32767))
    #    self.src.raw[self.i2] = val
    #    self.src.raw[self.i2 + 1] = val
    left = property(_getleft, _setleft)
    right = property(_getright, _setright)
