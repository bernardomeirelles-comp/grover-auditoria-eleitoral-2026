"""Reconta RDV e BU de todos os membros por HTTP multipart Range, sem logs."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
import csv,hashlib,json,time,urllib.request,re,gzip,sys,traceback
from planejar_ranges import entries,groups
from benchmark_rdv import extract,compare
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'recontagem-nacional';OUT.mkdir(exist_ok=True)

def fetch(url,gs,modified):
 ranges=','.join(f"{g['start']}-{g['end']-1}" for g in gs)
 req=urllib.request.Request(url,headers={'Range':'bytes='+ranges,'If-Unmodified-Since':modified})
 for attempt in range(3):
  try:
   with urllib.request.urlopen(req,timeout=60) as r:
    assert r.status==206,'Download integral proibido'
    ct=r.headers.get('Content-Type','');expected=sum(g['end']-g['start'] for g in gs)
    data=r.read(expected+len(gs)*1024+1024)
    assert len(data)<=expected+len(gs)*1024,'Resposta excedeu limite'
    if len(gs)==1:
     assert len(data)==expected;return [(gs[0],data)],len(data)
    assert 'multipart/byteranges' in ct,ct
    boundary=ct.split('boundary=',1)[1].strip().strip('"').encode();parts={}
    for part in data.split(b'--'+boundary)[1:-1]:
     assert part.startswith(b'\r\n') and part.endswith(b'\r\n');head,body=part[2:-2].split(b'\r\n\r\n',1)
     m=re.search(rb'Content-Range: bytes (\d+)-(\d+)/(\d+)',head,re.I);assert m
     start,end=map(int,m.group(1,2));assert len(body)==end-start+1
     assert start not in parts;parts[start]=body
    assert set(parts)=={g['start'] for g in gs}
    return [(g,parts[g['start']]) for g in gs],len(data)
  except Exception:
   if attempt==2:raise
   time.sleep(attempt+1)

def run(uf,limit=None):
 resultpath=OUT/f'{uf}-resumo.json'
 if resultpath.exists() and not limit:return json.loads(resultpath.read_text())
 meta=json.loads((ROOT/f'inventario-{uf}.json').read_text());es=entries(uf);gs=groups(es,gap=0)
 if limit:gs=gs[:limit]
 pairs={};total=Counter();origins=Counter();types=Counter();errors=[];count=0;bytesread=0;requests=0;beg=time.monotonic()
 output=OUT/f'{uf}{"-benchmark" if limit else ""}-secoes.csv.gz'
 fields=['stem','municipio','zona','secao','comparecimento','rdv_13','rdv_22','rdv_95','rdv_96','bu_13','bu_22','bu_95','bu_96','tipo_rdv','origens','sha256_rdv','sha256_bu']
 with gzip.open(output,'wt',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for start in range(0,len(gs),64):
   stamp=time.monotonic();chunks,n=fetch(meta['url'],gs[start:start+64],meta['last_modified']);bytesread+=n;requests+=1
   for g,data in chunks:
    for e in g['entries']:
     stem=e['name'].split('-',1)[0];kind='rdv' if e['name'].endswith('-rdv.dat') else 'bu'
     try:
      b=extract(data,g['start'],e);pair=pairs.setdefault(stem,{})
      assert kind not in pair;pair[kind]=b
      if len(pair)==2:
       r=compare(pair['rdv'],pair['bu']);ident=r['identificacao'];v=r['votos']
       row=dict(stem=stem,municipio=ident['municipioZona']['municipio'],zona=ident['municipioZona']['zona'],secao=ident['secao'],comparecimento=r['comparecimento'],tipo_rdv=r['tipo_rdv'],origens='|'.join(r['origens']),sha256_rdv=hashlib.sha256(pair['rdv']).hexdigest(),sha256_bu=hashlib.sha256(pair['bu']).hexdigest())
       for code in [13,22,95,96]:row[f'rdv_{code}']=row[f'bu_{code}']=v.get(code,0)
       w.writerow(row);total.update(v);origins.update(r['origens']);types[r['tipo_rdv']]+=1;count+=1;del pairs[stem]
     except Exception as ex:
      errors.append(dict(stem=stem,error=repr(ex)));pairs.pop(stem,None)
   # Máximo20 requisições/s por processo; quatro processos no máximo.
   delay=.05-(time.monotonic()-stamp)
   if delay>0:time.sleep(delay)
   if requests%25==0:print(uf,count,'seções',requests,'requisições',flush=True)
 duration=time.monotonic()-beg
 result=dict(uf=uf,benchmark=bool(limit),url=meta['url'],last_modified=meta['last_modified'],central_sha256=meta['central_sha256'],secoes_recontadas=count,votos=dict(total),origens=dict(origins),tipos=dict(types),erros=errors,pares_incompletos=list(pairs),requests=requests,bytes_recebidos=bytesread,segundos=duration,sha256_csv=hashlib.sha256(output.read_bytes()).hexdigest(),assinaturas_nacionais_verificadas=False)
 (OUT/f'{uf}{"-benchmark" if limit else ""}-resumo.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result),flush=True)
 return result
if __name__=='__main__':
 args=sys.argv[1:]
 if args and args[0]=='benchmark':run('AC',256)
 else:
  ufs=args or [x['uf'] for x in json.loads((ROOT/'diretorios-zip.json').read_text())]
  with ProcessPoolExecutor(max_workers=4) as pool:results=list(pool.map(run,ufs))
  if not args:(OUT/'resultados-ufs.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
