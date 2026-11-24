"""Publish only the explicitly authorized, independently verified Windows bytes.

Runs in the public distribution repository with its scoped GitHub job token.
No app installation, private profile, Android manifest, OTA or merge is used.
"""
from pathlib import Path
from zipfile import ZipFile
from hashlib import file_digest
import json,os,shutil,subprocess
REPO='Nrzxl/hanna-conquest-downloads';TAG='v26.1.11'
SOURCE='b1f1a9d1de7d814729b16a61eb43f3149ed67fd1'
TARGET='486481dac0934447eceea78fa670f1ecb49130e8'
EXPECTED={'HANNA_R6_26_1_11_MAIN_PROGRAM_UPDATE_WINDOWS.zip':'e036561f71905076dfe9c4d3a09f6ade1ff1a982eb4c4d6bc6898f996eb1fc84',
    'HANNA_conquest_Setup_R6_26_1_11_x64.exe':'d514747c8b2cebb61e6cb07148fdc48912b7bc74a63805fd0b6200d20ca06f1e',
    'HANNA_CONQUEST_R6_MAIN_26_1_11_WINDOWS.zip':'39405b76aefd466595ed81958bb56bf81ebbbfae8353241cebae86829a0cd15e'}
def digest(path):
    with path.open('rb') as f:return file_digest(f,'sha256').hexdigest()
def gh(*args):
    p=subprocess.run(['gh',*args],capture_output=True,text=True,check=True)
    return p.stdout
def api(path):return json.loads(gh('api','repos/'+REPO+'/'+path))
def main():
    assert os.environ.get('GITHUB_REPOSITORY')==REPO
    proof=json.loads(Path('ci/windows-26.1.11-final-verification.json').read_text(encoding='utf8'))
    assert proof['authorization']['authorized'] is True
    qa=proof['exactDownloadQA'];assert qa['status']=='PASS' and qa['PASS']==14 and qa['FAIL']==0
    assert qa['standardExeJourney']=='21/21' and not qa['callbackErrors']
    assert qa['exactSetupSHA256']==EXPECTED['HANNA_conquest_Setup_R6_26_1_11_x64.exe']
    assert qa['exactDeltaSHA256']==EXPECTED['HANNA_CONQUEST_R6_MAIN_26_1_11_WINDOWS.zip']
    # Distribution is program-only. A local disk shortage blocks installation,
    # not publication of bytes whose installer already enforces that reserve.
    # No storage margin or installer guard is changed here.
    assert proof['storage']['status'] in ('PASS','BLOCKED') and proof['storage']['personalDataChanged'] is False
    assert proof['storage']['installerRechecksBeforeApplying'] is True
    reserves={row['volume']:row['reserve'] for row in proof['storage']['volumes']}
    assert reserves=={'C:':7651259719,'D:':8589934592}
    assert proof['deployment_verified'] is False and proof['personal_sync_activation_allowed'] is False
    run=api('actions/runs/45307569591')
    assert run['conclusion']=='success' and run['head_sha']==TARGET
    incoming=Path('verified-input');receipt=json.loads((incoming/'CI_OFFICIAL_RECEIPT.json').read_text())
    assert receipt['CIaffectedTests']==58 and receipt['CIinstaller']=='PASS'
    assert receipt['credentialMatches']==receipt['personalDataFiles']==0
    assert receipt['deployment_verified'] is False and receipt['personal_sync_activation_allowed'] is False
    bundle=incoming/'HANNA_R6_26_1_11_MAIN_PROGRAM_UPDATE_WINDOWS.zip'
    assert bundle.stat().st_size==62612707 and digest(bundle)==EXPECTED[bundle.name]
    out=Path('release_upload');out.mkdir()
    with ZipFile(bundle) as z:
        assert z.testzip() is None
        inventory=json.loads(z.read('MANIFEST_SHA256.json'))
        assert set(z.namelist())==set(inventory)|{'MANIFEST_SHA256.json'}
        for name,pin in inventory.items():
            with z.open(name) as f:assert file_digest(f,'sha256').hexdigest()==pin
        for name in EXPECTED:
            if name==bundle.name:continue
            with z.open(name) as source,(out/name).open('wb') as target:shutil.copyfileobj(source,target)
            assert digest(out/name)==EXPECTED[name]
    shutil.copy2(bundle,out/bundle.name)
    with ZipFile(out/'HANNA_CONQUEST_R6_MAIN_26_1_11_WINDOWS.zip') as z:
        assert z.testzip() is None
        release=json.loads(z.read('HANNA_R6_MAIN/release.json'))
        assert release['channel']=='stable' and release['version']=='26.1.11'
        assert release['personal_install_allowed'] is True
        assert release['deployment_verified'] is False and release['personal_sync_activation_allowed'] is False
    shutil.copy2('ci/windows-26.1.11-final-verification.json',out/'FINAL_VERIFICATION.json')
    checksums={p.name:digest(p) for p in out.iterdir() if p.is_file()}
    (out/'SHA256SUMS.txt').write_text(''.join(pin+'  '+name+'\n' for name,pin in sorted(checksums.items())))
    notes='''Atualização oficial somente do programa HANNA conquest Windows R6 26.1.9 para 26.1.11, na mesma instalação.

Baixe o Setup x64 para a primeira transição. Feche a HANNA, execute o instalador e use “Fazer backup e atualizar”, mantendo D:\\HANNA como destino do backup. O perfil, as configurações, artes, contas e instalação anterior são preservados. Não desinstale a versão atual.

O Sync está integrado ao programa, mas a importação e a sincronização pessoal continuam desativadas e dependem de revisão/aprovação própria. deployment_verified=false até a validação física do usuário.

Validação: CI 58 PASS; 14 controles do pacote baixado PASS; jornada no EXE 21/21; CRC, manifestos e hashes conferidos; atualização, reaplicação, falha injetada e rollback verificados em QA isolado. Relatório completo em FINAL_VERIFICATION.json e no pacote com evidências. As provas históricas são identificadas separadamente.

O atualizador da 26.1.11 usa o GitHub público sem token para próximas versões. A 26.1.9 usa o transporte privado antigo: esta primeira transição deve ser feita pelo Setup, sem instalar um segundo aplicativo.

O EXE não possui assinatura Authenticode (NotSigned). Confira os SHA-256 fornecidos. Reservas de armazenamento não foram reduzidas; espaço insuficiente interrompe a atualização.

No computador de desenvolvimento, a instalação física ainda está bloqueada por espaço em C:. O programa está publicado, mas essa instalação deve aguardar a liberação segura de espaço. Nenhuma exclusão adicional de arquivos foi autorizada por esta publicação.

Sem alteração de OTA Android, merge, importação pessoal ou R7. Código revisado na PR #36, que permanece draft.
'''
    Path('release_notes.md').write_text(notes,encoding='utf8')
    existing=subprocess.run(['gh','release','view',TAG,'--repo',REPO,'--json','tagName'],capture_output=True,text=True)
    if existing.returncode==0:raise RuntimeError('Release already exists; inspect it before any retry. No overwrite.')
    gh('release','create',TAG,'--repo',REPO,'--target',TARGET,'--title','HANNA conquest Windows R6 26.1.11',
       '--notes-file','release_notes.md','--draft','--latest=false')
    files=[str(p) for p in sorted(out.iterdir()) if p.is_file()]
    gh('release','upload',TAG,*files,'--repo',REPO)
    published=api('releases/tags/'+TAG)
    assert published['draft'] is True and published['prerelease'] is False
    assets={a['name']:a for a in published['assets']}
    expected={p.name:digest(p) for p in out.iterdir() if p.is_file()}
    assert set(assets)==set(expected)
    for name,pin in expected.items():
        assert assets[name]['state']=='uploaded' and assets[name]['digest']=='sha256:'+pin
        assert assets[name]['size']==(out/name).stat().st_size
    gh('release','edit',TAG,'--repo',REPO,'--draft=false','--latest=false')
    result=api('releases/tags/'+TAG)
    assert result['draft'] is False and result['prerelease'] is False
    print(json.dumps(dict(status='PUBLISHED_PROGRAM_ONLY',release=result['html_url'],source=SOURCE,
        assets={a['name']:dict(bytes=a['size'],digest=a['digest']) for a in result['assets']},
        deployment_verified=False,personal_sync_activation_allowed=False)))
if __name__=='__main__':main()
