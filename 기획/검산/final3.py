"""20단계 구간안 최종 수치 검산: python3 final3.py"""
import sys, os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import sim3
from sim3 import *
N=300
def flow(name,checkins,**kw):
    res=[scenario(sd,checkins,**kw) for sd in range(N)]
    print('===',name)
    for k in list(range(1,21))+[('gate',1)]+list(range(21,41))+[('gate',2)]:
        rows=[S.first[k] for S,_ in res if k in S.first]
        ts=[r[0] for r in rows]
        print(f'{str(k):10} {st.median(ts):7.2f}h ({pct(ts,.1):6.2f}~{pct(ts,.9):6.2f}) Lv{st.median([r[1] for r in rows]):3.0f} P{st.median([r[2] for r in rows]):5.0f}')
    for g in (1,2):
        tr=[t[g] for S,t in res if t[g]]
        print(f'관문{g} 도전 횟수 중앙 {st.median([len(x) for x in tr])}, 첫 도전 승률 {sum(x[0][2] for x in tr)/len(tr):.0%}, 첫 패배 잔여 {st.median([x[0][3] for x in tr if not x[0][2]] or [0])}%')
if __name__=='__main__':
    print('need',[need(L) for L in range(1,41)])
    c=0
    for L in range(1,41): c+=need(L); print(f'{L+1}:{c}',end=' ')
    print()
    for s in range(1,41): print(s,R(s),T(s),round(XR(s)*T(s)),round(GOLD(s)*T(s)),'%.1f'%(0.25*60/T(s)))
    e3=[3*x for x in range(1,200)]
    flow('A 3시간마다',e3)
    flow('B 첫날 0.25/3/6/12h 이후 하루 2회',[0.25,3,6,12]+[12*k for k in range(2,40)])
    flow('E 동급 2인',e3,party=2)
    print('=== 관문 미토벌 대기')
    for h in (3.5,6,12,24,48,72,168):
        Ps=[];Ls=[];ss=[]
        for sd in range(N):
            S=Sim(sd); S.until(h); Ps.append(S.p()); Ls.append(S.L)
            S.clear_gate(1); ss.append(S.s)
        print(f'{h}h Lv{st.median(Ls)} P{st.median(Ps)} ({pct(Ps,.1)}~{pct(Ps,.9)}) 관문1 대비 {st.median(Ps)/10:.0f}% 토벌직후 {st.median(ss)}단계')
    print('=== 관문2 앞 대기 (3시간마다로 관문1 통과 후)')
    for extra in (0,6,12,24,48):
        Ps=[]
        for sd in range(N):
            S=Sim(sd)
            while S.s<20: S.step()
            while not boss_fight([S.stats()],1000)[0]: S.step()
            S.clear_gate(1)
            while S.s<40: S.step()
            S.until(S.t/60+extra); Ps.append(S.p())
        print(f'40단계 도착 +{extra}h P{st.median(Ps)} 관문2 대비 {st.median(Ps)/25:.0f}%')
    sim3.CFG['gate_supply']=False
    print('관문 앞 보급 없음:',quick(60))
    sim3.CFG['gate_supply']=True
    print('관문 앞 보급 있음:',quick(60))
    for a,b in ((2000,1000),(2500,800),(1800,600)):
        print('관문2 도움',a,b,boss_fight([(a/10,a),(b/10,b)],2500)[:2])
    print('관문2 동급2인 2250',boss_fight([(225,2250)]*2,2500)[:2])
