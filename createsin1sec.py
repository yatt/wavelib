import sys
import wavelib

def main():
    freq = 440
    if len(sys.argv) > 1:
        freq = int(sys.argv[1])
    
    info = wavelib.WaveInfo(1, 8, 44100, 44100)
    init = wavelib.SinWaveInit(freq)
    wave = wavelib.Wave(info, init)
    
    print 'generate sin wave freq=%dHz' % freq
    wave.play()
    wave.saveas('out.wav')


if __name__ == '__main__':
    main()
