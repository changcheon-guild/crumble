"""직업(전사·사냥꾼·성직자) 검산. python3 classes.py
직업 보정은 최종 공격력·체력에 곱한다. 혼자일 때 같은 전투력이면 같은 결과가 나오게 맞췄다.
성직자는 '보호': 파티가 받는 피해를 28% 줄인다(여럿이어도 겹치지 않음)."""
import math
CLS={'전사':(0.6,1/0.6,0),'사냥꾼':(1.6,0.625,0),'성직자':(0.8,0.9,0.28)}
def member(cls,P):   # 같은 전투력 P(직업 보정 전 기준 A=P/10, H=P)
    a,h,r=CLS[cls]; return (P/10*a, P*h, r)
def fight(ms, ehp, edps):
    red=max(m[2] for m in ms); edps*= (1-red)
    hp=[m[1] for m in ms]; sec=0; full=ehp
    while sec<600:
        sec+=1
        for i,m in enumerate(ms):
            if hp[i]>0: ehp-=m[0]
        if ehp<=0: return True,sec,ehp
        alive=[i for i in range(len(ms)) if hp[i]>0]; tot=sum(ms[i][1] for i in alive)
        for i in alive: hp[i]-=edps*ms[i][1]/tot
        if all(x<=0 for x in hp): return False,sec,ehp/full
    return False,sec,ehp/full
def boss(team,Rg=1000): return fight([member(c,p) for c,p in team],3*Rg,0.03*Rg)
def shown(team):
    """화면에 보여줄 파티 전투력 = √(10 × ΣA × ΣH ÷ (1 − 보호))"""
    ms=[member(c,p) for c,p in team]; A=sum(m[0] for m in ms); H=sum(m[1] for m in ms); r=max(m[2] for m in ms)
    return math.floor(math.sqrt(10*A*H/(1-r)))
def solo_display(cls,P): return shown([(cls,P)])
if __name__=='__main__':
    print('혼자일 때 표시 전투력(기준 1000):',{c:solo_display(c,1000) for c in CLS})
    for c in CLS:
        thr=next(p for p in range(800,1100) if boss([(c,p)])[0])
        print(c,'솔로 첫 관문 승리 최소(기준 전투력)',thr)
    teams=[[('전사',1000),('전사',1000)],[('전사',1000),('사냥꾼',1000)],[('전사',1000),('성직자',1000)],[('사냥꾼',1000),('성직자',1000)],
           [('성직자',1000),('성직자',1000)],[('전사',1000),('사냥꾼',1000),('성직자',1000)],[('전사',1000),('사냥꾼',1000),('성직자',1000),('사냥꾼',1000)],
           [('전사',1000),('사냥꾼',1000),('성직자',1000),('전사',1000)],[('사냥꾼',1000)]*4]
    for t in teams:
        s=sum(p for _,p in t); d=shown(t)
        print('+'.join(c for c,_ in t),'합계',s,'표시',d,f'보너스 {d/s-1:+.0%}')
    # 표시 전투력이 승패를 정확히 예측하는지: 표시값 기준 938 근처에서 확인
    import itertools
    bad=0; n=0
    for comp in [('전사','사냥꾼'),('전사','성직자'),('사냥꾼','성직자'),('전사','사냥꾼','성직자'),('사냥꾼','사냥꾼'),('성직자','전사','전사','사냥꾼')]:
        for p in range(150,700,5):
            team=[(c,p) for c in comp]; d=shown(team); w=boss(team)[0]; n+=1
            if (d>=945 and not w) or (d<930 and w): bad+=1; print('불일치',comp,p,d,w)
    print('표시 전투력 예측 검사',n,'건 중 불일치',bad)
    # 첫 관문 도착 시점(925) 두 명
    for comp in [('전사','전사'),('전사','성직자')]:
        print(comp,'각 470',boss([(c,470) for c in comp]),'표시',shown([(c,470) for c in comp]))
