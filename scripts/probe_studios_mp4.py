"""Read MP4 timing, sample count, codec and H.264 SPS chroma without external tools."""
from pathlib import Path
import argparse
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('movie')
parser.add_argument('--manifest', help='Optional editorial trial format manifest')
args = parser.parse_args()
expected = json.loads(Path(args.manifest).read_text()) if args.manifest else {'frames':720,'duration_seconds':30,'fps':24,'resolution':[1920,1080]}
path = Path(args.movie).resolve()
if not path.is_relative_to(ROOT):
    raise ValueError('Movie must be inside this video workspace')
data = path.read_bytes()
u32 = lambda offset: struct.unpack_from('>I', data, offset)[0]
u64 = lambda offset: struct.unpack_from('>Q', data, offset)[0]

def boxes(start, end):
    while start + 8 <= end:
        size, kind = u32(start), data[start+4:start+8].decode('ascii', errors='replace')
        header = 8
        if size == 1:
            size, header = u64(start+8), 16
        elif size == 0:
            size = end-start
        if size < header or start+size > end:
            raise ValueError(f'Invalid MP4 box {kind} at {start}')
        yield kind, start+header, start+size
        start += size

def child(parent, kind):
    return next(box for box in boxes(parent[1], parent[2]) if box[0] == kind)

def pixel_format(avcc):
    pos = avcc[1]
    if data[pos+5] & 31 < 1:
        raise ValueError('Missing AVC sequence parameter set')
    length = struct.unpack_from('>H', data, pos+6)[0]
    nal = data[pos+8:pos+8+length]
    raw, zeroes = bytearray(), 0
    for value in nal[1:]:
        if zeroes >= 2 and value == 3:
            zeroes = 0
            continue
        raw.append(value)
        zeroes = zeroes+1 if value == 0 else 0
    bits = ''.join(f'{value:08b}' for value in raw)
    cursor = 24
    def ue():
        nonlocal cursor
        zeroes = 0
        while bits[cursor] == '0':
            cursor += 1
            zeroes += 1
        value = int(bits[cursor:cursor+zeroes+1], 2)-1
        cursor += zeroes+1
        return value
    ue()  # seq_parameter_set_id
    profile = raw[0]
    chroma, depth_luma, depth_chroma = 1, 8, 8
    if profile in (100, 110, 122, 244, 44, 83, 86, 118, 128, 138, 139, 134, 135):
        chroma = ue()
        if chroma == 3:
            cursor += 1
        depth_luma, depth_chroma = ue()+8, ue()+8
    return {'profile_idc': profile, 'chroma_format_idc': chroma,
            'bit_depth_luma': depth_luma, 'bit_depth_chroma': depth_chroma,
            'pixel_format': 'yuv420p' if (chroma, depth_luma, depth_chroma) == (1, 8, 8) else 'other'}

moov = next(box for box in boxes(0, len(data)) if box[0] == 'moov')
tracks = []
for track in boxes(moov[1], moov[2]):
    if track[0] != 'trak':
        continue
    media = child(track, 'mdia')
    handler = child(media, 'hdlr')
    kind = data[handler[1]+8:handler[1]+12].decode('ascii')
    info = {'type': kind}
    if kind == 'vide':
        mdhd = child(media, 'mdhd')[1]
        version = data[mdhd]
        scale = u32(mdhd+(20 if version else 12))
        duration = u64(mdhd+24) if version else u32(mdhd+16)
        table = child(child(media, 'minf'), 'stbl')
        desc = child(table, 'stsd')
        sample = next(boxes(desc[1]+8, desc[2]))
        width, height = struct.unpack_from('>HH', data, sample[1]+24)
        count = u32(child(table, 'stsz')[1]+8)
        timing = child(table, 'stts')[1]
        entries = [struct.unpack_from('>II', data, timing+8+8*i) for i in range(u32(timing+4))]
        info.update(codec=sample[0], width=width, height=height, frames=count,
                    duration_seconds=duration/scale, fps=count*scale/duration,
                    constant_frame_rate=len({delta for _, delta in entries}) == 1)
        if sample[0] in ('avc1', 'avc3'):
            avcc = next(box for box in boxes(sample[1]+78, sample[2]) if box[0] == 'avcC')
            info.update(pixel_format(avcc))
    tracks.append(info)
video = next(track for track in tracks if track['type'] == 'vide')
passed = (len(tracks) == 1 and video['codec'] in ('avc1', 'avc3') and video['frames'] == expected['frames']
          and video['duration_seconds'] == expected['duration_seconds'] and video['fps'] == expected['fps'] and video['constant_frame_rate']
          and [video['width'], video['height']] == expected['resolution'] and video['pixel_format'] == 'yuv420p')
report = {'movie': str(path), 'bytes': path.stat().st_size, 'tracks': tracks,
          'audio_present': any(track['type'] == 'soun' for track in tracks), 'passed': passed}
output = ROOT / f'logs/probe-{path.stem}.json'
if output.exists():
    raise RuntimeError(f'Preserving existing report: {output}')
output.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
if not passed:
    raise RuntimeError('MP4 does not match required delivery format')
