"""첫 관문 상세 검산: 방 구성, 보스, 필살기, 파티. python3 gate1.py"""
import math
def fight(members, ehp, edps, ult=False, ult_gauge=12, ult_mult=3):
    """members: [(A,H,hp_now)], 매초 생존자 공격 → 적 생존 시 반격(균등 분배). 필살기: 게이지 찰 때마다 3×A 추가(수동, 누르자마자 사용 가정)"""
    hp=[m[2] for m in members]; sec=0
    while sec<600:
        sec+=1
        for i,(a,h,_) in enumerate(members):
            if hp[i]>0:
                ehp-=a
                if ult and sec%ult_gauge==0: ehp-=ult_mult*a
        if ehp<=0: return True,sec,hp
        alive=[i for i in range(len(hp)) if hp[i]>0]
        for i in alive: hp[i]-=edps/len(alive)
        if all(x<=0 for x in hp): return False,sec,hp
    return False,sec,hp
R=1000
ROOMS=[('입구 무리',0.6*R,0.02*R),('안쪽 방 정예',0.8*R,0.03*R)]
BOSS=(3*R,0.03*R)
def run(Ps, ult=False):
    mem=[(p/10,p,p) for p in Ps]; t=0
    for name,hp_,d in ROOMS:
        win,sec,hp=fight(mem,hp_,d)
        t+=sec
        if not win: return f'{name}에서 패배',t
        mem=[(a,h,max(0,x)) for (a,h,_),x in zip(mem,hp)]
    mem=[(a,h,h) for a,h,_ in mem]   # 보스 방 앞 휴식처: 생명력 가득
    win,sec,hp=fight(mem,*BOSS,ult=ult)
    t+=sec
    return ('승리' if win else '보스에게 패배'),t,sec
def thr(ult):
    for p in range(500,1100):
        r=run([p],ult)
        if r[0]=='승리': return p
print('방만 통과하는 최소 전투력', next(p for p in range(300,1000) if '입구' not in run([p])[0] and '안쪽' not in run([p])[0]))
print('솔로 승리 최소 전투력: 필살기 없음',thr(False),'/ 필살기 사용',thr(True))
for Ps in ([900],[940],[1000],[1200],[1500],[925,925],[1300,600],[500,500],[300,300,300,300],[2500,800]):
    print(Ps, run(Ps), '필살기', run(Ps,True))
