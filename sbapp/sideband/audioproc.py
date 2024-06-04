import os
import io
import sh
import math
import time
import struct
import numpy as np
import RNS
import LXMF

if RNS.vendor.platformutils.is_android():
    from pyogg import OpusFile, OpusBufferedEncoder, OggOpusWriter
    from pydub import AudioSegment
else:
    if RNS.vendor.platformutils.is_linux():
        from sbapp.pyogg import OpusFile, OpusBufferedEncoder, OggOpusWriter
    else:
        from pyogg import OpusFile, OpusBufferedEncoder, OggOpusWriter

    from sbapp.pydub import AudioSegment

codec2_modes = {
    # LXMF.AM_CODEC2_450PWB: ???, # No bindings
    # LXMF.AM_CODEC2_450: ???,    # No bindings
    LXMF.AM_CODEC2_700C: 700,
    LXMF.AM_CODEC2_1200: 1200,
    LXMF.AM_CODEC2_1300: 1300,
    LXMF.AM_CODEC2_1400: 1400,
    LXMF.AM_CODEC2_1600: 1600,
    LXMF.AM_CODEC2_2400: 2400,
    LXMF.AM_CODEC2_3200: 3200,
}

def samples_from_ogg(file_path=None, output_rate=8000):
    if file_path != None and os.path.isfile(file_path):
        opus_file = OpusFile(file_path)
        audio = AudioSegment(
            bytes(opus_file.as_array()),
            frame_rate=opus_file.frequency,
            sample_width=opus_file.bytes_per_sample, 
            channels=opus_file.channels)

        audio = audio.split_to_mono()[0]
        audio = audio.apply_gain(-audio.max_dBFS)
        audio = audio.set_frame_rate(output_rate)
        audio = audio.set_sample_width(2)
        
        return audio.get_array_of_samples()

def resample(samples, width, channels, input_rate, output_rate, normalize):
    audio = AudioSegment(
        samples,
        frame_rate=input_rate,
        sample_width=width,
        channels=channels)

    if normalize:
        audio = audio.apply_gain(-audio.max_dBFS)

    resampled_audio = audio.set_frame_rate(output_rate)
    return resampled_audio.get_array_of_samples().tobytes()

def samples_to_ogg(samples=None, file_path=None, normalize=False, input_channels=1, input_sample_width=2, input_rate=8000, output_rate=12000, profile="audio"):
    try:
        if file_path != None and samples != None:
            if input_rate != output_rate or normalize:
                samples = resample(samples, input_sample_width, input_channels, input_rate, output_rate, normalize)

            pcm_data = io.BytesIO(samples)
            channels = input_channels; samples_per_second = output_rate; bytes_per_sample = 2
            frame_duration_ms = 60

            opus_buffered_encoder = OpusBufferedEncoder()
            opus_buffered_encoder.set_application(profile)
            opus_buffered_encoder.set_sampling_frequency(samples_per_second)
            opus_buffered_encoder.set_channels(channels)
            opus_buffered_encoder.set_frame_size(frame_duration_ms)
            ogg_opus_writer = OggOpusWriter(file_path, opus_buffered_encoder)

            frame_duration = frame_duration_ms/1000.0
            frame_size = int(frame_duration * samples_per_second)
            bytes_per_frame = frame_size*bytes_per_sample
            
            ogg_opus_writer.write(memoryview(bytearray(samples)))
            ogg_opus_writer.close()
            
            return True
    
    except Exception as e:
        RNS.trace_exception(e)
        return False

def samples_to_wav(samples=None, file_path=None):
    if samples != None and file_path != None:
        import wave
        with wave.open(file_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(8000)
            wf.writeframes(samples)
        return True

def voice_processing(input_path):
    try:
        ffmpeg = None
        ffmpeg = sh.ffmpeg
        if ffmpeg:
            filters = "highpass=f=250, lowpass=f=3000,speechnorm=e=12.5:r=0.0001:l=1"
            output_bitrate = "12k"
            opus_apptype = "audio"
            output_path = input_path.replace(".ogg","")+".p.ogg"
            args = [
                "-i", input_path, "-filter:a", filters,
                "-c:a", "libopus", "-application", opus_apptype,
                "-vbr", "on","-b:a", output_bitrate, output_path]
            try:
                try:
                    os.unlink(output_path)
                except:
                    pass
                ffmpeg(*args)
                return output_path
            except Exception as e:
                RNS.log("Could not process audio with ffmpeg", RNS.LOG_ERROR)
                RNS.trace_exception(e)
                return None

    except Exception as e:
        return None

def detect_codec2():
    try:
        import pycodec2
        return True
    except Exception as e:
        RNS.log("Could not import codec2 module, libcodec2 is probably not installed or available", RNS.LOG_ERROR)
        RNS.trace_exception(e)

    return False

# Samples must be 8KHz, 16-bit, 1 channel
def encode_codec2(samples, mode):
    ap_start = time.time()
    import pycodec2
    if not mode in codec2_modes:
        return None

    c2 = pycodec2.Codec2(codec2_modes[mode])
    SPF = c2.samples_per_frame()
    PACKET_SIZE = SPF * 2 # 16-bit samples
    STRUCT_FORMAT = '{}h'.format(SPF)
    F_FRAMES = len(samples)/SPF
    N_FRAMES = math.floor(len(samples)/SPF)
    # TODO: Add padding to align to whole frames
    frames = np.array(samples[0:N_FRAMES*SPF], dtype=np.int16)
    
    encoded = b""
    for pi in range(0, N_FRAMES):
        pstart = pi*SPF
        pend = (pi+1)*SPF
        frame = frames[pstart:pend]
        encoded_packet = c2.encode(frame)
        encoded += encoded_packet

    ap_duration = time.time() - ap_start
    RNS.log("Codec2 encoding complete in "+RNS.prettytime(ap_duration)+", bytes out: "+str(len(encoded)), RNS.LOG_DEBUG)

    return encoded

def decode_codec2(encoded_bytes, mode):
    ap_start = time.time()
    import pycodec2
    if not mode in codec2_modes:
        return None

    c2 = pycodec2.Codec2(codec2_modes[mode])
    SPF = c2.samples_per_frame()
    BPF = c2.bytes_per_frame()
    STRUCT_FORMAT = '{}h'.format(SPF)
    N_FRAMES = math.floor(len(encoded_bytes)/BPF)

    decoded = b""
    for pi in range(0, N_FRAMES):
        pstart = pi*BPF
        pend = (pi+1)*BPF
        encoded_packet = encoded_bytes[pstart:pend]
        decoded_frame = c2.decode(encoded_packet)
        decoded += struct.pack(STRUCT_FORMAT, *decoded_frame)

    ap_duration = time.time() - ap_start
    RNS.log("Codec2 decoding complete in "+RNS.prettytime(ap_duration)+", samples out: "+str(len(decoded)), RNS.LOG_DEBUG)

    return decoded