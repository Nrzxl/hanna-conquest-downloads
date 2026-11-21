"""Reconstruct the authorized original QA ZIP; never compile or run its app."""
from datetime import datetime, timezone
from hashlib import sha1, sha256
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
import json, re, stat

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / 'qa-windows-payload/manifest.json').read_text(encoding='utf8'))
NAME = 'HANNA_WINDOWS_SYNC_INTEGRATION_QA_20261120.zip'
SIZE = 61346960
PIN = 'adec09b75a34365f4b27b2b792e9b7eeecf13ffac895136428f6c6f13f86f2fe'
assert SPEC['file'] == NAME and SPEC['bytes'] == SIZE and SPEC['sha256'] == PIN
assert SPEC['deployment_verified'] is False
parts = SPEC['parts']
assert [p['index'] for p in parts] == list(range(118))
assert len({p['path'] for p in parts}) == 118
assert sum(p['size'] for p in parts) == SIZE

delivery = ROOT / 'qa-windows-delivery'
delivery.mkdir(exist_ok=False)
partial = delivery / (NAME + '.partial')
with partial.open('xb') as target:
    for p in parts:
        assert p['path'] == f"qa-windows-payload/part-{p['index']:03}.bin"
        raw = (ROOT / p['path']).read_bytes()
        assert len(raw) == p['size']
        assert sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest() == p['sha']
        target.write(raw)
assert partial.stat().st_size == SIZE
assert sha256(partial.read_bytes()).hexdigest() == PIN

with ZipFile(partial) as archive:
    assert archive.testzip() is None, 'CRC mismatch'
    names = archive.namelist()
    assert len(names) == len(set(names)) == 6676
    assert sum(p.file_size for p in archive.infolist()) < 512 * 1024**2
    for p in archive.infolist():
        path = PurePosixPath(p.filename)
        assert not path.is_absolute() and '..' not in path.parts and '\\' not in p.filename
        assert stat.S_IFMT(p.external_attr >> 16) != stat.S_IFLNK
        assert not p.filename.lower().endswith(('.dpapi', '.sqlite', '.sqlite3', '.db', '.pfx', '.pem', '.key'))
        assert '/private_observer/' not in p.filename and '/auth/' not in p.filename
    manifest = json.loads(archive.read('MANIFEST_SHA256.json'))
    assert set(names) == set(manifest) | {'MANIFEST_SHA256.json'}
    for name, pin in manifest.items():
        assert re.fullmatch(r'[a-f0-9]{64}', pin)
        assert sha256(archive.read(name)).hexdigest() == pin, name
    config = json.loads(archive.read('app/sync_qa_config.json'))
    assert config['qaOnly'] is True and config['deployment_verified'] is False
    text_files = 0
    for name in names:
        if name.endswith(('.py', '.md', '.json', '.txt', '.cs', '.yaml', '.yml', '.ini', '.cfg')):
            text = archive.read(name).decode('utf8', errors='replace')
            text_files += 1
            assert not re.search(r'sb_secret_[A-Za-z0-9_-]{20,}|eyJ[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{20,}|henrry[^\s<>"\x27]*@(?:gmail\.com|cdisoftwares\.com\.br)', text, re.I)

final = partial.with_name(NAME)
partial.rename(final)
receipt = dict(status='PASS', file=NAME, bytes=SIZE, sha256=PIN, crc='PASS',
               partsVerified=118, manifestHashesVerified=len(manifest), entries=6676,
               textFilesScanned=text_files, credentialOrPersonalEmailMatches=0,
               personalDatabaseOrSessionFiles=0, rebuiltApplication=False,
               originalZipReconstructed=True, deployment_verified=False,
               observedAtUtc=datetime.now(timezone.utc).isoformat())
(delivery / 'PUBLICATION_CI_RECEIPT.json').write_text(json.dumps(receipt, indent=2), encoding='utf8')
(delivery / (NAME + '.sha256')).write_text(PIN + '  ' + NAME + '\n', encoding='ascii')
(delivery / 'COMECE_AQUI.txt').write_text(
    'HANNA Windows Sync Integration QA\n\n'
    'Este artifact contém o ZIP original do pacote. Extraia o ZIP do pacote para uma pasta e abra HANNA_Sync_Integration_QA.exe.\n'
    'Em Configurações → HANNA Sync, entre somente na conta QA já admitida.\n'
    'No Android, use HANNA Sync UI QA com login próprio na mesma conta QA.\n'
    'Crie uma coleção no Windows e confira no celular; renomeie no celular e confira no Windows. Feche e reabra ambos.\n'
    'Não é necessário copiar IDs, JSON ou executar comandos. Não abra nem importe seu perfil pessoal.\n'
    'Não há instalador de sistema, Release, OTA ou homologação pessoal. deployment_verified=false.\n', encoding='utf8')
print(json.dumps(receipt, sort_keys=True))
