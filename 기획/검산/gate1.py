"""첫 관문 상세 검산 (전부 자동 시뮬레이션, 수동 조작 없음). python3 gate1.py"""
SPLIT='hp'   # 보스 피해 분배: 'hp'(추천안) 또는 'equal'(이전 초안)
def fight(members, ehp, edps):
    """members: [(A,H,현재 생명력)]. 매초 생존 모험가가 공격하고, 적이 살아 있으면 반격(생존자에게 균등 분배)."""
    full=ehp; hp=[m[2] for m in members]; sec=0
    while sec<600:
        sec+=1
        for i,(a,h,_) in enumerate(members):
            if hp[i]>0: ehp-=a
        if ehp<=0: return True,sec,hp,0
        alive=[i for i in range(len(hp)) if hp[i]>0]
        if SPLIT=='equal':
            for i in alive: hp[i]-=edps/len(alive)
        else:   # 'hp': 최대 생명력에 비례해 나눔 (강한 사람이 더 많이 맞아 준다)
            tot=sum(members[i][1] for i in alive)
            for i in alive: hp[i]-=edps*members[i][1]/tot
        if all(x<=0 for x in hp): return False,sec,hp,ehp/full
    return False,sec,hp,ehp/full
R=1000
ROOMS=[('입구 무리',0.6*R,0.02*R),('안쪽 방 정예',0.8*R,0.03*R)]
BOSS=(3*R,0.03*R)
def run(Ps):
    mem=[(p/10,p,p) for p in Ps]; t=0
    for name,ehp,d in ROOMS:
        win,sec,hp,left=fight(mem,ehp,d); t+=sec
        if not win: return dict(결과=f'{name}에서 물러남',전투초=t)
        mem=[(a,h,max(0,x)) for (a,h,_),x in zip(mem,hp)]
    mem=[(a,h,h) for a,h,_ in mem]          # 보스 방 앞 휴식처: 생명력 회복
    win,sec,hp,left=fight(mem,*BOSS); t+=sec
    alive=[x/m[1] for x,m in zip(hp,mem)]
    return dict(결과='승리' if win else '패배',전투초=t,보스전초=sec,보스남은체력=f'{left:.0%}',
                남은생명력=f'{max(alive):.0%}' if win else '0%')
if __name__=='__main__':
    print('방 통과 최소 전투력', next(p for p in range(300,1000) if '물러남' not in run([p])['결과']))
    print('솔로 승리 최소 전투력', next(p for p in range(500,1100) if run([p])['결과']=='승리'))
    for Ps in ([600],[800],[850],[900],[925],[938],[1000],[1200],[1500],[2000],[925,925],[1300,600],[500,500],[400,400,400],[300,300,300,300],[250,250,250,250],[2500,800]):
        print(Ps, '합계',sum(Ps), run(Ps))
