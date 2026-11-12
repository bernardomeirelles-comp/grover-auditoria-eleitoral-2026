"""Inventário ZIP/ZIP64 por Range; não baixa conteúdo dos membros."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import Counter, defaultdict
import io,json,struct,urllib.request,zipfile,sys,hashlib,gzip
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent
SOURCES=[r for r in json.loads((ROOT.parent/'tamanhos-nacional-2026.json').read_text()) if r['dataset']=='resultados-2026-arquivos-transmitidos-para-totalizacao']
def read(url,start,end):
 req=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}'})
 with urllib.request.urlopen(req,timeout=60) as r:
  assert r.status==206,'Range obrigatório: download integral proibido'
  body=r.read(end-start+2)
  assert len(body)==end-start+1
  return body

def describe(s):
 n=s['size_bytes'];tail=read(s['url'],n-65557,n-1);i=tail.rfind(b'PK\x05\x06');assert i>=0
 e=struct.unpack_from('<4s4H2IH',tail,i);count=e[4];size=e[5];offset=e[6]
 if count==65535 or size==4294967295 or offset==4294967295:
  loc=struct.unpack_from('<4sIQI',tail,i-20);assert loc[0]==b'PK\x06\x07'
  off=loc[2];z=read(s['url'],off,off+55);v=struct.unpack('<4sQ2H2I4Q',z);assert v[0]==b'PK\x06\x06'
  count,size,offset=v[7],v[8],v[9]
 return dict(s,uf=s['url'].rsplit('_',1)[1].split('.')[0],entries=count,central_size=size,central_offset=offset)

def inventory(s):
 size=s['size_bytes'];offset=s['central_offset'];buf=read(s['url'],offset,size-1)
 entries=[];pos=0
 while pos<s['central_size']:
  v=struct.unpack_from('<4s6H3I5H2I',buf,pos);assert v[0]==b'PK\x01\x02'
  name=buf[pos+46:pos+46+v[10]].decode('utf-8' if v[3]&2048 else 'cp437')
  extra=buf[pos+46+v[10]:pos+46+v[10]+v[11]]
  usize,csize,hoff=v[9],v[8],v[16];epos=0
  while epos<len(extra):
   tag,sz=struct.unpack_from('<HH',extra,epos);data=extra[epos+4:epos+4+sz];epos+=4+sz
   if tag==1:
    q=0
    if usize==4294967295:usize=struct.unpack_from('<Q',data,q)[0];q+=8
    if csize==4294967295:csize=struct.unpack_from('<Q',data,q)[0];q+=8
    if hoff==4294967295:hoff=struct.unpack_from('<Q',data,q)[0];q+=8
  entries.append(SimpleNamespace(filename=name,compress_size=csize,file_size=usize,header_offset=hoff,CRC=v[7],compress_type=v[4]))
  pos+=46+v[10]+v[11]+v[12]
 assert len(entries)==s['entries'] and pos==s['central_size']
 stats=defaultdict(lambda:dict(count=0,compressed=0,uncompressed=0));sections=defaultdict(set)
 namecounts=Counter(e.filename for e in entries)
 with gzip.open(ROOT/f"membros-{s['uf']}.jsonl.gz",'wt') as f:
  for e in entries:
   suffix=e.filename.split('-',1)[1] if '-' in e.filename else e.filename
   stats[suffix]['count']+=1;stats[suffix]['compressed']+=e.compress_size;stats[suffix]['uncompressed']+=e.file_size
   stem=e.filename.split('-',1)[0];sections[stem].add(suffix)
   row=dict(name=e.filename,offset=e.header_offset,compressed=e.compress_size,size=e.file_size,crc=e.CRC,method=e.compress_type)
   f.write(json.dumps(row)+'\n')
 result=dict(s,central_sha256=hashlib.sha256(buf).hexdigest(),types=dict(stats),section_stems=len(sections),duplicate_names=[k for k,v in namecounts.items() if v>1],without_bu=sum('bu.dat' not in v for v in sections.values()),without_rdv=sum('rdv.dat' not in v for v in sections.values()),patterns=dict(Counter(','.join(sorted(v)) for v in sections.values())))
 (ROOT/f"inventario-{s['uf']}.json").write_text(json.dumps(result,indent=2))
 return result

if __name__=='__main__':
 path=ROOT/'diretorios-zip.json'
 if not path.exists():path.write_text(json.dumps(list(ThreadPoolExecutor(max_workers=4).map(describe,SOURCES)),indent=2))
 ds=json.loads(path.read_text());print('Entradas',sum(x['entries'] for x in ds),'diretórios bytes',sum(x['central_size'] for x in ds),flush=True)
 chosen=set(sys.argv[1:])
 for s in ds:
  if s['uf'] in chosen or 'ALL' in chosen:
   r=json.loads((ROOT/f"inventario-{s['uf']}.json").read_text()) if (ROOT/f"inventario-{s['uf']}.json").exists() else inventory(s);print(r['uf'],r['section_stems'],r['types'],r['patterns'],flush=True)
