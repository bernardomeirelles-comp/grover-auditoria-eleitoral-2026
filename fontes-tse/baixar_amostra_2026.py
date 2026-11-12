"""Obtém só a seção escolhida usando HTTP Range sobre o ZIP público do TSE."""
from pathlib import Path
import io
import json
import struct
import urllib.request
import zipfile
import zlib

ROOT = Path(__file__).resolve().parent
URL = 'https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/arqurnatot/bu_imgbu_logjez_rdv_vscmr_2026_2t_AC.zip'
STEM = 'o03221ac0100700090001'

def read_range(start, end):
    req = urllib.request.Request(URL, headers={'Range': f'bytes={start}-{end}'})
    with urllib.request.urlopen(req, timeout=30) as response:
        if response.status != 206:
            raise RuntimeError('Servidor não aceitou Range; download integral cancelado.')
        data = response.read(end - start + 2)
        assert len(data) == end - start + 1
        return data, dict(response.headers)

_, headers = read_range(0, 1023)
size = int(headers['Content-Range'].split('/')[-1])
start = max(0, size - 2000000)
tail, _ = read_range(start, size - 1)
entries = zipfile.ZipFile(io.BytesIO(tail)).infolist()
assert any(i.filename == STEM + '-bu.dat' for i in entries), 'Seção escolhida não encontrada'
manifest = []
for suffix in ('-bu.dat', '-rdv.dat', '-log.jez', '-vota.vsc'):
    entry = next(i for i in entries if i.filename == STEM + suffix)
    offset = entry.header_offset + start
    header, _ = read_range(offset, offset + 29)
    fields = struct.unpack('<4s5H3I2H', header)
    assert fields[0] == b'PK\x03\x04'
    begin = offset + 30 + fields[-2] + fields[-1]
    compressed, _ = read_range(begin, begin + entry.compress_size - 1)
    assert entry.compress_type in (0, 8)
    data = zlib.decompress(compressed, -15) if entry.compress_type == 8 else compressed
    assert len(data) == entry.file_size and zlib.crc32(data) == entry.CRC
    dest = ROOT / entry.filename
    if dest.exists() and dest.read_bytes() != data:
        raise RuntimeError(f'Arquivo de origem mudou: {dest.name}; original preservado.')
    dest.write_bytes(data)
    manifest.append(dict(filename=entry.filename, size=len(data), crc_verified=True, source_zip=URL, range_start=offset))
(ROOT / 'amostras-arquivos-2026.json').write_text(json.dumps(manifest, indent=2))
(ROOT / 'proveniencia-download.json').write_text(json.dumps(dict(url=URL, tecnica='HTTP Range: diretório ZIP e quatro entradas; pacote estadual não baixado integralmente.', data_consulta='2026-11-06 America/Sao_Paulo', tamanho_zip_estadual=size, headers=headers, arquivos=manifest), ensure_ascii=False, indent=2))
print('Quatro arquivos obtidos; os originais existentes foram conferidos.')
