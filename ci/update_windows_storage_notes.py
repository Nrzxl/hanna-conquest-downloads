"""Update only Release instructions after the authorized physical QA cleanup."""
from pathlib import Path
import json,os,subprocess
REPO='Nrzxl/hanna-conquest-downloads';RID=456641626
def api(*args):
    return json.loads(subprocess.run(['gh','api',*args],capture_output=True,text=True,check=True).stdout)
assert os.environ['GITHUB_REPOSITORY']==REPO
proof=json.loads(Path('qa/windows-r6-26.1.11/INSTALLATION_STORAGE_READY.json').read_text(encoding='utf8'))
assert proof['status']=='PASS' and proof['authorization']['authorized']
assert proof['authorization']['userAnswer']=='Autorizar somente essas sete cópias QA de C: e os dois registros QA'
assert all(v['status']=='PASS' and v['remainingAfterUpdate']>=v['reserve'] for v in proof['storage']['volumes'])
assert len(proof['archive']['copies'])==7 and proof['archive']['allProgramRecoveryCopiesPreservedInD']
assert proof['afterQACleanup']['BothQAKeysRemoved'] and proof['afterQACleanup']['PersonalVersion']=='26.1.9'
assert proof['personalInstallationWritten'] is False and proof['personal_sync_activation_allowed'] is False and proof['deployment_verified'] is False
release=api(f'repos/{REPO}/releases/{RID}')
assert release['tag_name']=='v26.1.11' and not release['draft'] and not release['prerelease']
before={a['name']:(a['size'],a['digest']) for a in release['assets']}
assert before['HANNA_conquest_Setup_R6_26_1_11_x64.exe']==(59627520,'sha256:d514747c8b2cebb61e6cb07148fdc48912b7bc74a63805fd0b6200d20ca06f1e')
assert before['HANNA_CONQUEST_R6_MAIN_26_1_11_WINDOWS.zip']==(1025331,'sha256:39405b76aefd466595ed81958bb56bf81ebbbfae8353241cebae86829a0cd15e')
old='No computador de desenvolvimento, a instalação física ainda está bloqueada por espaço em C:. O programa está publicado, mas essa instalação deve aguardar a liberação segura de espaço. Nenhuma exclusão adicional de arquivos foi autorizada por esta publicação.'
new='Armazenamento verificado em 24/11/2026: reservas C: e D: PASS, incluindo o custo da atualização e do backup. Após autorização específica, somente sete cópias antigas de programa QA foram retiradas de C:, todas preservadas e verificadas em D:, com os perfis e backups de dados intactos. A instalação pessoal continua 26.1.9, pronta para o usuário executar o Setup. O instalador reavalia o espaço antes de aplicar. Importação e Sync pessoal permanecem desativados; deployment_verified=false.'
body=release['body']
if old in body:body=body.replace(old,new)
else:assert new in body
link='https://github.com/Nrzxl/hanna-conquest-downloads/blob/qa/windows-r6-main-candidate-20261123/qa/windows-r6-26.1.11/DELIVERY_REPORT.md'
if link not in body:body+='\n\nRelatório final atualizado: '+link+'\n'
Path('release_notes_patch.json').write_text(json.dumps(dict(body=body)),encoding='utf8')
api('--method','PATCH',f'repos/{REPO}/releases/{RID}','--input','release_notes_patch.json')
after=api(f'repos/{REPO}/releases/{RID}')
assert before=={a['name']:(a['size'],a['digest']) for a in after['assets']}
assert not after['draft'] and not after['prerelease']
print(json.dumps(dict(status='RELEASE_NOTES_STORAGE_UPDATED',release=after['html_url'],assetsUnchanged=True,personalInstallationWritten=False,deployment_verified=False)))

