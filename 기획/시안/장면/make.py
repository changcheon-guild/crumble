from PIL import Image, ImageEnhance, ImageOps
import os
T='dl/pp/kenney_pixel-platformer/Tiles/'
def t(i): return Image.open(T+'tile_%04d.png'%i).convert('RGBA')
SKY=Image.open('assets_preview/sky_bg_paur/tilesetOpenGameBackground_1.png').convert('RGBA')
def sky(w,h,top=60): return SKY.crop((0,top,w,top+h)).copy()
def island(cols, rows, kind='grass'):
    """cols: 상단 너비(타일 수). 아래로 갈수록 양쪽이 한 칸씩 줄어듦."""
    top={'grass':(20,21,22,23),'snow':(100,101,102,103),'sand':(60,61,62,63)}[kind]
    W=cols*18; H=rows*18
    im=Image.new('RGBA',(W,H),(0,0,0,0))
    for r in range(rows):
        inset=r if r>0 else 0
        c0=inset; c1=cols-1-inset
        if c1<c0: break
        last = (r==rows-1) or (c1-1-1 < c0+1)
        for c in range(c0,c1+1):
            if r==0: idx= top[0] if c==c0 else (top[3] if c==c1 else top[1+(c%2)])
            elif last: idx= 140 if c==c0 else (143 if c==c1 else 141+(c%2))
            else: idx= 120 if c==c0 else (123 if c==c1 else 121+(c%2))
            im.paste(t(idx),(c*18,r*18),t(idx))
        if last: break
    return im
def put(scene, img, x, y): scene.paste(img,(x,y),img)
def spr(path): return Image.open(path).convert('RGBA')
OUT='scenes/'
CH='outline/'
# 1. 새벽 구름 지대
s=sky(195,130,70)
put(s, island(3,2), 8, 40)
put(s, island(4,3), 150, 26)
main=island(7,4); put(s, main, 52, 70)
for i,x in ((126,62),(124,98),(128,140),(125,156)): put(s,t(i),x,52)
put(s,t(97),118,34); put(s,t(117),118,52)
put(s, spr(CH+'ranger_noline.png'), 82, 54)
put(s, spr(CH+'slime_noline.png'), 104, 54)
s.save(OUT+'zone1.png')
# 2. 비구름 지대 (서늘한 눈덮인 섬 + 폭포, 하늘을 조금 어둡게)
s=sky(195,130,70); s=ImageEnhance.Color(s).enhance(0.55); s=ImageEnhance.Brightness(s).enhance(0.85)
put(s, island(3,2,'snow'), 150, 30)
main=island(7,4,'snow'); put(s, main, 30, 66)
for y in (102,120): put(s,t(54 if y==102 else 74),66,y)
put(s,t(126),48,48); put(s,t(126),136,48)
put(s, spr(CH+'knight_noline.png'), 84, 50)
put(s, spr(CH+'crab_noline.png'), 106, 50)
s.save(OUT+'zone2.png')
# 3. 잿빛 폭풍 지대 (모래 섬을 잿빛으로, 마른 나무)
s=sky(195,130,70); s=ImageEnhance.Color(s).enhance(0.15); s=ImageEnhance.Brightness(s).enhance(0.7)
main=island(8,4,'sand'); main=ImageEnhance.Color(main).enhance(0.25)
put(s, main, 24, 64)
small=ImageEnhance.Color(island(3,2,'sand')).enhance(0.25); put(s, small, 158, 34)
for x in (40,150): put(s,t(116),x,46); put(s,t(136),x,46+0)
put(s, spr(CH+'wizard_noline.png'), 92, 48)
put(s, spr(CH+'bat_noline.png'), 118, 40)
s.save(OUT+'zone3.png')
for n in ('zone1','zone2','zone3'):
    im=Image.open(OUT+n+'.png'); im.resize((im.width*2,im.height*2),Image.NEAREST).save(OUT+n+'@2x.png')
sheet=Image.new('RGBA',(390*3+20,260),(16,22,31,255))
for i,n in enumerate(('zone1','zone2','zone3')): sheet.paste(Image.open(OUT+n+'@2x.png'),(i*400,0))
sheet.save(OUT+'compare.png')
