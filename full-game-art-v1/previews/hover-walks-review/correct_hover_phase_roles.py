from pathlib import Path
import json
R=Path(__file__).resolve().parents[2]
roles=['hover-left-sway-extreme','hover-passing-toward-right','hover-right-sway-extreme','hover-passing-toward-left']
n=0
for p in (R/'assets/motion-native/orig_mob03').glob('*.generation.json'):
 v=json.loads(p.read_text(encoding='utf-8'));v['phaseRole']=roles[v['phase']];v['animationKind']='hover-walk'
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');n+=1
print(n,'lantern provenance phase roles corrected to hover')
