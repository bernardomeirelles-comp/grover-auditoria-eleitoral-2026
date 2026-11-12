from pathlib import Path
import gzip,json
ROOT=Path(__file__).resolve().parent

def entries(uf):return sorted((json.loads(l) for l in gzip.open(ROOT/f'membros-{uf}.jsonl.gz','rt')),key=lambda e:e['offset'])
def groups(allentries,gap=262144,maxsize=8*1024*1024):
 selected=[]
 for i,e in enumerate(allentries):
  if e['name'].endswith(('-bu.dat','-busa.dat','-rdv.dat')):
   # Include local header and compressed payload; next header bounds exact entry.
   end=allentries[i+1]['offset'] if i+1<len(allentries) else e['offset']+e['compressed']+1024
   selected.append((e['offset'],end,e))
 result=[]
 for start,end,e in selected:
  if result and start-result[-1]['end']<=gap and end-result[-1]['start']<=maxsize:
   result[-1]['end']=end;result[-1]['entries'].append(e)
  else:result.append(dict(start=start,end=end,entries=[e]))
 return result
if __name__=='__main__':
 ds=json.loads((ROOT/'diretorios-zip.json').read_text());out={}
 for gap in [0,65536,262144,1048576]:
  count=total=0
  for d in ds:
   gs=groups(entries(d['uf']),gap);count+=len(gs);total+=sum(g['end']-g['start'] for g in gs)
  out[str(gap)]=dict(requests=count,bytes=total)
 print(out);(ROOT/'planos-ranges.json').write_text(json.dumps(out,indent=2))
