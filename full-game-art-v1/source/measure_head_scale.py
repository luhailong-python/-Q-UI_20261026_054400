"""Measure rigid head/helmet camera scale, independently from legs or pose bbox."""
from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[1]
def bbox(im):return im.getchannel('A').point(lambda v:255 if v>=16 else 0).getbbox()
def gray(im):
 a=np.asarray(im.convert('RGBA')).astype(np.float32);return (a[:,:,:3]@np.array([.299,.587,.114],dtype=np.float32))*a[:,:,3]/255
def patch(arr,cx,top,w,h,extra=0):
 x=round(cx-w/2)-extra;y=round(top)-extra;ww=w+2*extra;hh=h+2*extra
 out=np.zeros((hh,ww),np.float32);sx0=max(x,0);sy0=max(y,0);sx1=min(x+ww,arr.shape[1]);sy1=min(y+hh,arr.shape[0])
 if sx1>sx0 and sy1>sy0:out[sy0-y:sy1-y,sx0-x:sx1-x]=arr[sy0:sy1,sx0:sx1]
 return out
def max_ncc(template,search):
 windows=np.lib.stride_tricks.sliding_window_view(search,template.shape);t=template-template.mean();den=float(np.sqrt((t*t).sum()));v=windows-windows.mean(axis=(-2,-1),keepdims=True);scores=(v*t).sum(axis=(-2,-1))/np.maximum(np.sqrt((v*v).sum(axis=(-2,-1)))*den,1e-8)
 pos=np.unravel_index(np.argmax(scores),scores.shape);return float(scores[pos]),list(map(int,pos))
def measure(review):
 imgs=[Image.open(R/f).convert('RGBA') for f in review['selectedFiles']];b=[bbox(i) for i in imgs];anchors=review['anchors'];a0=anchors[0].get('sourceAnchorXY',[anchors[0].get('sourceTorsoX'),anchors[0].get('sourceGroundY')]);bodyheight=b[0][3]-b[0][1]
 unit=.125;w=max(24,round(bodyheight*.28*unit));h=max(24,round(bodyheight*.25*unit));topoffset=bodyheight*.10*unit
 first=gray(imgs[0].resize((round(imgs[0].width*unit),round(imgs[0].height*unit)),Image.Resampling.LANCZOS));template=patch(first,a0[0]*unit,b[0][1]*unit+topoffset,w,h)
 records=[{'phase':0,'relativeHeadScale':1.0,'score':1.0,'applied':False,'reason':'reference rigid head/helmet phase'}]
 for k in range(1,4):
  a=anchors[k].get('sourceAnchorXY',[anchors[k].get('sourceTorsoX'),anchors[k].get('sourceGroundY')]);curve=[]
  for factor in np.linspace(.84,1.30,47):
   s=unit*float(factor);small=imgs[k].resize((round(imgs[k].width*s),round(imgs[k].height*s)),Image.Resampling.LANCZOS);arr=gray(small);search=patch(arr,a[0]*s,b[k][1]*s+topoffset,w,h,extra=8);score,pos=max_ncc(template,search);curve.append({'factor':round(float(factor),3),'score':score,'offsetYX':[pos[0]-8,pos[1]-8]})
  best=max(curve,key=lambda v:v['score']);baseline=min(curve,key=lambda v:abs(v['factor']-1));applied=best['score']>=.65 and best['score']-baseline['score']>=.015 and abs(best['factor']-1)>=.015
  records.append({'phase':k,'relativeHeadScale':best['factor'] if applied else 1.0,'bestCandidateFactor':best['factor'],'score':best['score'],'scoreAt1':baseline['score'],'scoreImprovement':best['score']-baseline['score'],'applied':applied,'reason':'Rigid head/helmet template scale fit; legs, ground and full-body bbox are excluded from scale score','curve':curve})
 for record in records:record['suggested']=record.pop('applied');record['applied']=False
 return {'actor':review['actor'],'selectedFiles':review['selectedFiles'],'referencePhase':0,'method':'NCC analysis of head/helmet interior at1/8resolution; translation search±8analysispx; no whole-body/leg-bbox height normalization','templateSize':[w,h],'headRegionRelativeTop':[.10,.35],'records':records,'approvedByVisualReview':False,'rejectionReason':'Automated template can confuse changed head pose/ornament placement with camera zoom. Actual contact review rejected automatic large factors; final export retains one common scale unless separately explicitly approved.','needsVisualReview':True,'notMotionGeneration':True}
def main():
 out=[]
 for p in sorted((R/'records/motion').glob('*-native-review.json')):
  v=json.loads(p.read_text(encoding='utf-8-sig'))
  if v.get('passed') and not v.get('blockingIssues'):out.append(measure(v))
 (R/'records/motion-head-calibration.json').write_text(json.dumps({'scope':'Tentative technical camera-zoom correction from head only, not anatomical pose scaling','actors':out},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps([{'actor':v['actor'],'factors':[x['relativeHeadScale'] for x in v['records']],'scores':[round(x['score'],3) for x in v['records']]} for v in out],ensure_ascii=False))
if __name__=='__main__':main()
