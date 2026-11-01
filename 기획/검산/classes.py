"""직업(전사·사냥꾼·마법사) 검산: 조합 보너스 없이 역할만 나누기. python3 classes.py
원칙: 모든 직업의 '공격 기여 : 생존 기여' = 1 : 10. 역할은 기여의 모양만 바꾼다.
- 전사: 보스 공격을 2배로 끌어오고(도발), 받는 피해를 절반으로 막는다(방어).
- 사냥꾼: 자기 공격력으로만 기여(가장 큰 피해 숫자).
- 마법사: 고른 마법에 따라 기여 모양이 바뀐다.
    공격 마법 = 자기 공격, 치유 마법 = 생존 기여 일부를 파티 보호막으로, 강화 마법 = 공격 기여 일부를 동료 공격력으로."""
import math, itertools
def member(cls,P,heal=0.0,buff=0.0):
    A=P/10; H=P
    return dict(cls=cls,A=A*(1-buff),H=H*(1-heal),shield=H*heal,buff=A*buff)
def fight(ms, ehp, edps):
    hp=[m['H'] for m in ms]; n=len(ms)
    shield=sum(m['shield'] for m in ms)            # 치유 마법: 전투 시작 시 파티 보호막
    buff=sum(m['buff'] for m in ms)                # 강화 마법: 동료 공격력에 나눠 더함
    sec=0; full=ehp
    while sec<600:
        sec+=1
        alive=[i for i in range(n) if hp[i]>0]
        ehp-=sum(ms[i]['A'] for i in alive)+ (buff if alive else 0)
        if ehp<=0: return True,sec
        d=edps
        if shield>0:
            use=min(shield,d); shield-=use; d-=use
        # 피해 분배: 생명력 비례, 전사는 2배로 끌어오고 절반만 받음 → 실제 받는 비율은 생명력 비례와 같다
        w={i:ms[i]['H']*(2 if ms[i]['cls']=='전사' else 1) for i in alive}; tot=sum(w.values())
        for i in alive:
            hit=d*w[i]/tot
            hp[i]-=hit*(0.5 if ms[i]['cls']=='전사' else 1)
        # 전사 절반 방어로 남는 피해를 비전사에게 다시 나누지 않도록 보정: 정규화
        if any(ms[i]['cls']=='전사' for i in alive):
            took=sum(d*w[i]/tot*(0.5 if ms[i]['cls']=='전사' else 1) for i in alive)
            scale=d/took if took else 1
            # 실제 받는 총 피해가 d가 되도록 맞춘다(방어는 '모양'일 뿐 총량은 같음)
            for i in alive:
                hit=d*w[i]/tot*(0.5 if ms[i]['cls']=='전사' else 1)
                hp[i]-=hit*(scale-1)
        if all(x<=0 for x in hp): return False,sec
    return False,sec
def boss(team,Rg=1000): return fight([member(*t) for t in team],3*Rg,0.03*Rg)
if __name__=='__main__':
    forms=[('전사',),('사냥꾼',),('마법사',0,0),('마법사',0.3,0),('마법사',0,0.3),('마법사',0.15,0.15)]
    bad=0;n=0
    for size in (1,2,3,4):
        for comp in itertools.combinations_with_replacement(forms,size):
            for tot in (900,930,945,960,1000):
                P=tot/size; team=[(f[0],P)+tuple(f[1:]) for f in comp]
                w=boss(team)[0]; n+=1
                if (tot>=945 and not w) or (tot<=930 and w): bad+=1; print('불일치',comp,tot,w)
    print('합계 예측 검사',n,'건 중 불일치',bad)
    # 피해 받는 몫 (전사+사냥꾼+마법사, 각 1000)
    ms=[member('전사',1000),member('사냥꾼',1000),member('마법사',1000)]
    w=[m['H']*(2 if m['cls']=='전사' else 1) for m in ms]; print('보스 공격이 향하는 비율',[f'{x/sum(w):.0%}' for x in w])
