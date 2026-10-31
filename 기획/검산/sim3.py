"""20단계 구간 + 관문 버전 성장 시뮬레이션 (수치 초안 검산용)"""
import math, random, statistics as st
Z=20                                   # 관문 간격
def R(s): return round(900*2.5**((s-Z)/Z))          # 원정 권장 전투력
def gateR(g): return round(1000*2.5**(g-1))         # 관문 권장 전투력 1,000 / 2,500 / 6,250
def P(A,H): return math.floor(math.sqrt(10*A*H))
def G(i): return 10*2.5**((i-1)/Z)                  # 일반 3부위 합계 공격력
GR=[('일반',1.00,0.62),('고급',1.15,0.28),('희귀',1.35,0.085),('영웅',1.60,0.014),('전설',2.00,0.001)]
SL=['무기','방어구','장신구']
def item(slot,i,g):
    u=G(i)*GR[g][1]
    return {'무기':(0.6*u,0),'방어구':(0,6*u),'장신구':(0.4*u,4*u)}[slot]
CFG=dict(xr_base=12, xr_c=1.07, need_a=10, need_b=2.7, drop=0.25, gate_supply=False)
EARLY={1:10,2:25,3:50,4:90}
def need(L): return EARLY.get(L, round(CFG['need_a']*L**CFG['need_b']))
def XR(s): return CFG['xr_base']*CFG['xr_c']**(s-1)
def GOLD(s): return 20*1.06**(s-1)
def T(s,first=False):
    if first: return 0.5
    if s<=2: return 1.0
    if s<=20: return 2+(s-3)*0.25          # 3단계 2분 … 20단계 6.25분
    return min(10, 6.5+(s-21)*0.2)        # 21단계 6.5분 … 39단계 이후 10분
def lvstat(L): return 30+5*(L-1),300+50*(L-1)
def boss_fight(members,Rg):
    bhp=3*Rg; bd=0.03*Rg; hp=[h for a,h in members]; sec=0
    while sec<600:
        sec+=1
        for i,(a,h) in enumerate(members):
            if hp[i]>0: bhp-=a
        if bhp<=0: return True,sec,0
        alive=[i for i in range(len(hp)) if hp[i]>0]
        for i in alive: hp[i]-=bd/len(alive)
        if all(x<=0 for x in hp): return False,sec,bhp/(3*Rg)
    return False,sec,bhp/(3*Rg)
class Sim:
    def __init__(S,seed):
        S.rnd=random.Random(seed); S.L=1; S.xp=0; S.s=1; S.t=0.0; S.gold=0; S.runs=0
        S.eq={k:(1,0) for k in SL}; S.opened=1; S.first={1:(0,1,400)}
    def stats(S):
        A,H=lvstat(S.L)
        for k,(i,g) in S.eq.items():
            a,h=item(k,i,g); A+=a; H+=h
        return A,H
    def p(S): return P(*S.stats())
    def offer(S,slot,i,g):
        old=S.p(); prev=S.eq[slot]; S.eq[slot]=(i,g)
        if S.p()<=old: S.eq[slot]=prev
    def advance(S):
        while S.s<Z*S.opened and S.p()>=R(S.s+1):
            S.s+=1; S.first.setdefault(S.s,(S.t/60,S.L,S.p()))
    def step(S):
        dt=T(S.s,S.runs==0); S.t+=dt; S.runs+=1
        S.xp+=XR(S.s)*dt; S.gold+=GOLD(S.s)*dt
        while S.xp>=need(S.L): S.xp-=need(S.L); S.L+=1
        if S.runs==1: S.offer('무기',S.s,1)
        if S.runs==2: S.offer('방어구',S.s,1)
        if S.rnd.random()<CFG['drop']:
            slot=S.rnd.choice(SL); r=S.rnd.random(); acc=0
            for gi,(n,m,pp) in enumerate(GR):
                acc+=pp
                if r<acc: break
            ilv=S.s+1 if (CFG['gate_supply'] and S.s==Z*S.opened) else S.s
            S.offer(slot,ilv,gi)
        S.advance()
    def until(S,h):
        while S.t<h*60: S.step()
    def clear_gate(S,g):
        S.opened=g+1; S.offer('무기',Z*g+1,2)
        S.first.setdefault(('gate',g),(S.t/60,S.L,S.p())); S.advance()
def pct(xs,q): xs=sorted(xs); return xs[min(len(xs)-1,int(q*len(xs)))]
def scenario(seed,checkins,party=1,delay=None):
    S=Sim(seed); tries={1:[],2:[]}
    for c in checkins:
        S.until(c)
        for g in (1,2):
            if S.opened==g and S.s==Z*g and (delay is None or c>=delay):
                win,sec,left=boss_fight([S.stats()]*party,gateR(g))
                tries[g].append((c,S.p(),win,round(left*100)))
                if win: S.clear_gate(g)
    return S,tries
def quick(seeds=60):
    out={k:[] for k in ('L10m','s10m','arr1','solo1','arr2','solo2')}
    for sd in range(seeds):
        S=Sim(sd); S.until(1/6); out['L10m'].append(S.L); out['s10m'].append(S.s)
        while S.s<Z: S.step()
        out['arr1'].append(S.t/60)
        while not boss_fight([S.stats()],gateR(1))[0]: S.step()
        out['solo1'].append(S.t/60); S.clear_gate(1)
        while S.s<2*Z and S.t<600*60: S.step()
        out['arr2'].append(S.t/60)
        while not boss_fight([S.stats()],gateR(2))[0] and S.t<900*60: S.step()
        out['solo2'].append(S.t/60)
    return {k:round(st.median(v),2) for k,v in out.items()}
