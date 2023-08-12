import io
import struct

import miditk.smf


_HMP_HEADER_LENGTH = 0x30
_HMP_TEMPO = 1605632 # 60 000 000 / 1 605 632 ~~ 37.368 bpm
_HMP_TRACK_DIVISION = 192
_SMF_1_FORMAT = 1


def export_as_smf(hmp_data: bytes) -> bytes:
    track_count = hmp_data[_HMP_HEADER_LENGTH]
    track_end = hmp_data.find(b'\xff\x2f', 0)
    if track_end < 0:
        raise Exception("Corrupted HMP data")
    sizeaddr = track_end + 7
    with io.BytesIO() as f:
        mfw = miditk.smf.MidiFileWriter(f)
        mfw.header(format=_SMF_1_FORMAT, num_tracks=track_count, tick_division=_HMP_TRACK_DIVISION)
        mfw.start_of_track()
        mfw.tempo(_HMP_TEMPO)
        mfw.end_of_track()
        for _ in range(1, track_count):
            mfw.start_of_track()
            mfw.update_ticks(0, True)
            track_size = struct.unpack("I", hmp_data[sizeaddr:sizeaddr+4])[0] - 12
            track_start = sizeaddr + 8
            track_end = track_start + track_size
            sizeaddr = track_end + 4
            current_timestamp = 0
            i = track_start
            while i < track_end:
                delta = 0
                shift = 0
                while True:
                    b = hmp_data[i]
                    i = i + 1
                    delta = delta + ((b & 0x7F) << shift)
                    shift = shift + 7
                    if b & 0x80:
                        break
                current_timestamp = current_timestamp + delta
                status = hmp_data[i]
                if status == 0xff:
                    i = i + 1
                    data = [0xff, hmp_data[i]]
                    i = i + 1
                    meta_count = 0
                    while True:
                        b = hmp_data[i]
                        i = i + 1
                        meta_count = (meta_count << 7) + (b & 0x7F)
                        if not (b & 0x80):
                            break
                    for x in range(0, meta_count):
                        data.append(hmp_data[i + x])
                    i = i + meta_count
                    mfw.update_ticks(delta)
                    if hmp_data == [0xff, 0x2f]:
                        break
                    mfw.meta_slice(data[1], bytes(data[2:]))
                elif 0x80 <= status <= 0xef:
                    data = []
                    event_type = (status >> 4) - 8
                    channel = status & 0x0f
                    if status & 0xf0 in [0xc0, 0xd0]:
                        data = [hmp_data[i + 1]]
                        i = i + 2
                    else:
                        data = [b for b in hmp_data[i+1:i+3]]
                        i = i + 3
                    mfw.update_ticks(delta)
                    mfw.event_slice(bytes([status] + data))
                else:
                    raise Exception("Corrupted HMP data")
            mfw.end_of_track()
        mfw.eof()
        midi_data = f.getvalue()
    return midi_data
