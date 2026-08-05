from .simulator import simulate_design
from .verifier import verify_result

def evaluate_mission(climate, candidates, constraints):
    if not candidates: raise ValueError('at least one candidate is required')
    rows=[]
    for design in candidates:
        result=simulate_design(climate, design, constraints)
        verification=verify_result(result)
        rows.append({'design':design.name,'simulation':result.to_dict(),'verification':{'approved':verification.approved,'checks':verification.checks,'message':verification.message}})
    ranked=sorted(rows,key=lambda x:(x['verification']['approved'],x['simulation']['score']),reverse=True)
    winner=ranked[0] if ranked[0]['verification']['approved'] else None
    return {'mission_status':'CUMPLIDA' if winner else 'IMPUGNADA','winner':winner,'ranked_candidates':ranked}
