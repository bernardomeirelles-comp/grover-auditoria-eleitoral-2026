"""Confere SHA512 dos arquivos; não verifica assinatura ou cadeia de certificados."""
from pathlib import Path
import hashlib
import json
import asn1tools

root = Path(__file__).resolve().parent
stem = 'o03221ac0100700090001'
codec = asn1tools.compile_files(str(root / 'spec/assinatura.asn1'), codec='ber')
envelope = codec.decode('EntidadeAssinaturaEcourna', (root / (stem + '-vota.vsc')).read_bytes())
rows = []
for field in ('assinaturaSW', 'assinaturaHW'):
    entity = envelope[field]
    encoded = entity['conteudoAutoAssinado']
    assert hashlib.sha512(encoded).digest() == entity['autoAssinado']['assinatura']['hash']
    decoded = codec.decode('Assinatura', encoded)
    for entry in decoded['arquivosAssinados']:
        name = entry['nomeArquivo']
        if name not in [stem + suffix for suffix in ('-bu.dat', '-rdv.dat', '-log.jez')]:
            continue
        expected = entry['assinatura']['hash']
        assert hashlib.sha512((root / name).read_bytes()).digest() == expected
        rows.append(dict(envelope=field, arquivo=name, sha512_confere=True, sha512=expected.hex()))
assert len(rows) == 6
(root / 'hashes-envelope-2026.json').write_text(json.dumps(dict(verificacao='SHA512 comparado ao hash no envelope SW/HW; assinatura criptográfica e cadeia de certificados não verificadas.', resultados=rows), ensure_ascii=False, indent=2))
print('SHA512 de BU, RDV e log confere nos envelopes SW e HW.')
