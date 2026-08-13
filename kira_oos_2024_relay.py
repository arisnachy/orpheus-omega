from __future__ import annotations
import hashlib, io, json, math
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse
import pandas as pd
import requests
from bs4 import BeautifulSoup

OUT=Path('kira_oos_2024_output'); OUT.mkdir(exist_ok=True)
START=date(2024,1,1); END=date(2024,12,31)
UA={'User-Agent':'Mozilla/5.0 KIRA-WORLD-FOOTBALL-EXPANSION-V1/1.0'}
PRIMARY_GROUPS={
'AUT':('Austria','https://www.football-data.co.uk/austria.php'),
'DNK':('Denmark','https://www.football-data.co.uk/denmark.php'),
'GRE':('Greece','https://www.football-data.co.uk/greecem.php'),
'MEX':('Mexico','https://www.football-data.co.uk/mexico.php'),
'POL':('Poland','https://www.football-data.co.uk/poland.php'),
'TUR':('Turkey','https://www.football-data.co.uk/turkeym.php'),
'ROU':('Romania','https://www.football-data.co.uk/romania.php'),
'SWZ':('Switzerland','https://www.football-data.co.uk/switzerland.php')}
LEG_RATE_GATE=0.965489; TWO_LEG_RATE_GATE_STRICT=0.90; MIN_LEGS=80; MIN_TWO_LEG_DATES=40
SOURCE_ALGORITHM={'run_oos_2024.py_blob':'18934f9027a49b34fb3065cb3800cee33cda8bb6','run_full6_r1.py_blob':'3fa3d20ba264b02eae20a3f9d88b7c3f1d8c24ad'}

def get(url,timeout=60):
 r=requests.get(url,headers=UA,timeout=timeout); r.raise_for_status(); return r

def sha(b): return hashlib.sha256(b).hexdigest()
def pick(df,names):
 m={str(c).strip().lower():c for c in df.columns}
 return next((m[n.lower()] for n in names if n.lower() in m),None)

def normalize(raw,league,code):
 cs=[pick(raw,['Date']),pick(raw,['Home','HomeTeam','Home Team']),pick(raw,['Away','AwayTeam','Away Team']),pick(raw,['HG','FTHG','HomeGoals','Home Goals']),pick(raw,['AG','FTAG','AwayGoals','Away Goals'])]
 if any(c is None for c in cs): return None
 d=raw[cs].copy(); d.columns=['Date','HomeTeam','AwayTeam','FTHG','FTAG']
 d['date']=pd.to_datetime(d['Date'],dayfirst=True,errors='coerce'); d['FTHG']=pd.to_numeric(d.FTHG,errors='coerce'); d['FTAG']=pd.to_numeric(d.FTAG,errors='coerce')
 d=d[d.date.notna()&d.FTHG.notna()&d.FTAG.notna()&d.HomeTeam.notna()&d.AwayTeam.notna()].copy()
 d=d[(d.date.dt.date>=START)&(d.date.dt.date<=END)].copy()
 if d.empty:return None
 d['league']=league; d['league_code']=code
 return d[['date','league','league_code','HomeTeam','AwayTeam','FTHG','FTAG']]

def links(page,html):
 s=BeautifulSoup(html,'html.parser'); out=[]
 for a in s.find_all('a',href=True):
  u=urljoin(page,a['href']); p=urlparse(u)
  if p.scheme in {'http','https'} and p.netloc.lower() in {'www.football-data.co.uk','football-data.co.uk'} and '.csv' in p.path.lower(): out.append(u)
 return list(dict.fromkeys(out))

def acquire():
 manifest={}; payloads={}
 for code,(league,page) in PRIMARY_GROUPS.items():
  e={'league':league,'page':page,'page_sha256':None,'csv_links':[],'csv_files':[],'errors':[]}; payloads[code]=[]
  try:
   b=get(page).content; e['page_sha256']=sha(b); e['csv_links']=links(page,b)
  except Exception as x:
   e['errors'].append(f'page:{type(x).__name__}:{x}'); manifest[code]=e; continue
  for u in e['csv_links']:
   try:
    b=get(u).content; e['csv_files'].append({'url':u,'sha256':sha(b),'bytes':len(b),'fetch_ok':True}); payloads[code].append((u,b))
   except Exception as x:e['csv_files'].append({'url':u,'sha256':None,'bytes':0,'fetch_ok':False,'error':f'{type(x).__name__}:{x}'})
  if not e['csv_links']:e['errors'].append('NO_CSV_LINKS_DISCOVERED')
  manifest[code]=e
 (OUT/'source_manifest_pre_score.json').write_text(json.dumps(manifest,indent=2,sort_keys=True))
 return manifest,payloads

def parse(manifest,payloads):
 frames=[]; audit={}
 for code,(league,_) in PRIMARY_GROUPS.items():
  gs=[]; errs=[]
  for u,b in payloads.get(code,[]):
   try:
    n=normalize(pd.read_csv(io.BytesIO(b),encoding_errors='ignore'),league,code)
    if n is not None:gs.append(n)
   except Exception as x:errs.append(f'{u}:{type(x).__name__}:{x}')
  if gs:
   g=pd.concat(gs,ignore_index=True).drop_duplicates(['date','league','HomeTeam','AwayTeam']); frames.append(g); nr=len(g)
  else:nr=0
  audit[code]={'league':league,'normalized_2024_rows':int(nr),'page_fetch_ok':bool(manifest.get(code,{}).get('page_sha256')),'csv_links_discovered':len(manifest.get(code,{}).get('csv_links',[])),'csv_files_fetched':sum(1 for x in manifest.get(code,{}).get('csv_files',[]) if x.get('fetch_ok')),'parse_errors':errs}
 (OUT/'source_parse_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True))
 if not frames:return pd.DataFrame(),audit
 m=pd.concat(frames,ignore_index=True).drop_duplicates(['date','league','HomeTeam','AwayTeam']).sort_values(['date','league','HomeTeam','AwayTeam']).reset_index(drop=True)
 return m,audit

def team_prior_stats(matches,team,target_ts):
 p=matches[(matches.date<target_ts)&((matches.HomeTeam==team)|(matches.AwayTeam==team))].sort_values('date')
 if p.empty:return None
 a=[]
 for _,r in p.iterrows():
  if r.HomeTeam==team:gf,ga=int(r.FTHG),int(r.FTAG)
  else:gf,ga=int(r.FTAG),int(r.FTHG)
  pts=3 if gf>ga else 1 if gf==ga else 0; a.append((pts,gf-ga))
 last=a[-5:]; n=len(a)
 return {'n':n,'ppg':sum(x[0] for x in a)/n,'gd_pg':sum(x[1] for x in a)/n,'last5_ppg':sum(x[0] for x in last)/len(last),'last5_gd_pg':sum(x[1] for x in last)/len(last),'loss3_rate':sum(1 for x in a if x[1]<=-3)/n}

def football_select(matches,target):
 ts=pd.Timestamp(target); today=matches[matches.date.dt.date==target]; c=[]
 for _,r in today.iterrows():
  lp=matches[(matches.league==r.league)&(matches.date<ts)]
  if lp.empty:continue
  appearances=2*len(lp); cat=int(((lp.FTHG-lp.FTAG)>=3).sum()+((lp.FTAG-lp.FTHG)>=3).sum()); lrate=cat/appearances if appearances else 0.0
  for team,opp,is_home,gf,ga in [(r.HomeTeam,r.AwayTeam,1,int(r.FTHG),int(r.FTAG)),(r.AwayTeam,r.HomeTeam,0,int(r.FTAG),int(r.FTHG))]:
   s=team_prior_stats(matches[matches.league==r.league],team,ts); o=team_prior_stats(matches[matches.league==r.league],opp,ts)
   if not s or not o or s['n']<8 or o['n']<8:continue
   if s['ppg']<1.50 or s['gd_pg']<0.25 or s['last5_ppg']<1.20 or s['loss3_rate']>0.10:continue
   strength=.45*s['ppg']+.25*s['gd_pg']+.15*s['last5_ppg']+.10*s['last5_gd_pg']+.05*is_home
   opp_home=1-is_home; ostr=.45*o['ppg']+.25*o['gd_pg']+.15*o['last5_ppg']+.10*o['last5_gd_pg']+.05*opp_home
   cri=ostr-strength+2.0*s['loss3_rate']+.5*lrate
   c.append({'team':team,'opponent':opp,'league':r.league,'home':bool(is_home),'season_ppg':s['ppg'],'season_gd_pg':s['gd_pg'],'last5_ppg':s['last5_ppg'],'last5_gd_pg':s['last5_gd_pg'],'prior_loss3_rate':s['loss3_rate'],'league_prior_loss3_rate':lrate,'cri':cri,'gf':gf,'ga':ga,'loss_margin':max(0,ga-gf)})
 c.sort(key=lambda x:(x['cri'],-x['season_ppg'],-x['season_gd_pg'],x['team']))
 return c[:2],c

def wilson(k,n,z=1.959963984540054):
 if not n:return None,None
 p=k/n; den=1+z*z/n; centre=(p+z*z/(2*n))/den; half=z*math.sqrt((p*(1-p)+z*z/(4*n))/n)/den
 return centre-half,centre+half

def main():
 manifest,payloads=acquire(); matches,audit=parse(manifest,payloads); loaded=[c for c,v in audit.items() if v['normalized_2024_rows']>0]
 if len(loaded)!=8:
  s={'experiment':'WORLD-FOOTBALL-EXPANSION-V1-OOS-2024','status':'DATA_MISSING','source_groups_loaded':loaded,'source_audit':audit,'algorithm_sources':SOURCE_ALGORITHM,'outcomes_scored':False}; (OUT/'summary.json').write_text(json.dumps(s,indent=2)); print(json.dumps(s)); return
 matches.to_csv(OUT/'normalized_source_rows.csv',index=False)
 daily=[]; legs=[]; d=START
 while d<=END:
  sel,univ=football_select(matches,d); v=[]
  for x in sel:
   y=dict(x); y['pass_plus_3_5']=int(y['loss_margin'])<4; v.append(y)
  two=len(v)==2; daily.append({'date':d.isoformat(),'matches_on_day':int((matches.date.dt.date==d).sum()),'eligible':len(univ),'selected':len(v),'two_leg_block':two,'two_leg_pass_plus_3_5':all(x['pass_plus_3_5'] for x in v) if two else None,'F1':v[0]['team'] if v else None,'F2':v[1]['team'] if len(v)>1 else None})
  for i,x in enumerate(v,1):legs.append({'date':d.isoformat(),'leg':f'WFV1_{i}','league':x['league'],'selected':x['team'],'opponent':x['opponent'],'home':x['home'],'cri':x['cri'],'season_ppg':x['season_ppg'],'season_gd_pg':x['season_gd_pg'],'last5_ppg':x['last5_ppg'],'last5_gd_pg':x['last5_gd_pg'],'prior_loss3_rate':x['prior_loss3_rate'],'league_prior_loss3_rate':x['league_prior_loss3_rate'],'loss_margin':x['loss_margin'],'pass_plus_3_5':x['pass_plus_3_5'],'detail_json':json.dumps(x,sort_keys=True)})
  d+=timedelta(days=1)
 daily=pd.DataFrame(daily); legs=pd.DataFrame(legs); daily.to_csv(OUT/'dates.csv',index=False); legs.to_csv(OUT/'legs.csv',index=False)
 two=daily[daily.two_leg_block==True]; tn=len(two); tw=int((two.two_leg_pass_plus_3_5==True).sum()); ln=len(legs); lw=int(legs.pass_plus_3_5.sum()) if ln else 0; tr=tw/tn if tn else None; lr=lw/ln if ln else None; tlo,thi=wilson(tw,tn); llo,lhi=wilson(lw,ln)
 sample=ln>=MIN_LEGS and tn>=MIN_TWO_LEG_DATES; observed=lr is not None and tr is not None and lr>=LEG_RATE_GATE and tr>TWO_LEG_RATE_GATE_STRICT
 status='OOS_PASS_CANDIDATE' if observed and sample else 'OOS_STRONG_SIGNAL_NOT_PROMOTABLE' if observed else 'OOS_NO_PASS'
 counts={str(int(k)):int(v) for k,v in daily.selected.value_counts().sort_index().to_dict().items()}; fails=legs[legs.pass_plus_3_5==False].to_dict('records') if ln else []
 by={}
 for league,g in legs.groupby('league') if ln else []:by[league]={'legs':len(g),'survived':int(g.pass_plus_3_5.sum()),'rate':float(g.pass_plus_3_5.mean()),'share_of_selected_legs':len(g)/ln}
 s={'experiment':'WORLD-FOOTBALL-EXPANSION-V1-OOS-2024','class':'FROZEN_WORLD_POPULATION_OOS','status':status,'preregistered_before_score':True,'algorithm_sources':SOURCE_ALGORITHM,'settlement':'selected_team_plus_3_5_goals','failure_event':'selected_team_loses_by_4_or_more','window':{'start':str(START),'end':str(END),'days':366},'source_groups_required':sorted(PRIMARY_GROUPS),'source_groups_loaded':sorted(loaded),'source_matches':len(matches),'daily_selected_count_distribution':counts,'days_with_two_leg_block':tn,'two_leg_blocks_survived':tw,'two_leg_block_survival_rate':tr,'two_leg_wilson95_lower':tlo,'two_leg_wilson95_upper':thi,'selected_legs':ln,'selected_leg_survivals':lw,'selected_leg_survival_rate':lr,'selected_leg_wilson95_lower':llo,'selected_leg_wilson95_upper':lhi,'frozen_gates':{'minimum_selected_legs':MIN_LEGS,'minimum_two_leg_dates':MIN_TWO_LEG_DATES,'selected_leg_survival_minimum':LEG_RATE_GATE,'two_leg_survival_strictly_greater_than':TWO_LEG_RATE_GATE_STRICT,'sample_gate_pass':sample,'observed_survival_gate_pass':observed},'by_league':by,'failure_legs':fails,'source_audit':audit,'integrity':{'odds_used_for_selection':False,'selector_changed_after_preregistration':False,'source_manifest_written_before_scoring':True,'maximum_daily_legs':2,'global_ranking_across_all_primary_groups':True,'production_promoted':False},'next_gate':'NO_PROMOTION_AUTOMATIC; prospective + exact Juancito +3.5 + price + dependence + JUDGE required'}
 (OUT/'summary.json').write_text(json.dumps(s,indent=2,default=str)); print('KIRA_OOS_SUMMARY='+json.dumps(s,default=str))
if __name__=='__main__':main()
