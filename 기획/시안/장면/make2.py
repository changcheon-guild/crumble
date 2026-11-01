"""화면 시안용 장면 합성. 재료: Kenney Pixel Platformer·Tiny Dungeon(CC0), PauR Sky background(CC BY 3.0), 갈무리9(OFL).
캐릭터·몬스터·이름표를 모두 한 장에 같은 배율로 넣는다. 화면에서는 2배·3배로만 키운다."""
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
T='dl/pp/kenney_pixel-platformer/Tiles/'
CH='outline/'
FONT=ImageFont.truetype('fonts/Galmuri9.ttf',10)
def t(i): return Image.open(T+'tile_%04d.png'%i).convert('RGBA')
def spr(n): return Image.open(CH+n+'_noline.png').convert('RGBA')
SKY=Image.open('assets_preview/sky_bg_paur/tilesetOpenGameBackground_1.png').convert('RGBA')
W,H=195,130
def base(tint=None, dark=1.0, sat=1.0):
    s=SKY.crop((0,70,W,70+H)).copy()
    if sat!=1.0: s=ImageEnhance.Color(s).enhance(sat)
    if tint: s=Image.alpha_composite(s,Image.new('RGBA',s.size,tint))
    if dark!=1.0: s=ImageEnhance.Brightness(s).enhance(dark)
    return s
def island(cols, rows, kind='grass'):
    """모양(위가 넓고 아래로 좁아짐)을 먼저 정하고, 칸마다 이웃이 없는 쪽에만 테두리가 있는 조각을 고른다."""
    fam={'grass':{'LRT':20,'LT':21,'T':22,'RT':23,'LRTB':0,'LTB':1,'TB':2,'RTB':3},
         'snow':{'LRT':100,'LT':101,'T':102,'RT':103,'LRTB':80,'LTB':81,'TB':82,'RTB':83},
         'sand':{'LRT':60,'LT':61,'T':62,'RT':63,'LRTB':40,'LTB':41,'TB':42,'RTB':43}}[kind]
    dirt={'LR':120,'L':121,'':122,'R':123,'LRB':140,'LB':141,'B':142,'RB':143}
    cells=set()
    for r in range(rows):
        c0=r; c1=cols-1-r
        if c1<c0: break
        for c in range(c0,c1+1): cells.add((c,r))
    im=Image.new('RGBA',(cols*18,rows*18),(0,0,0,0))
    for (c,r) in cells:
        k=('L' if (c-1,r) not in cells else '')+('R' if (c+1,r) not in cells else '')
        top=(c,r-1) not in cells; bot=(c,r+1) not in cells
        if top: idx=fam[k+'T'+('B' if bot else '')]
        else: idx=dirt[k+('B' if bot else '')]
        tile=t(idx); im.paste(tile,(c*18,r*18),tile)
    return im
def put(s,img,x,y): s.paste(img,(x,y),img)
def bottom(img):
    a=img.getchannel('A'); bb=a.getbbox(); return bb[3]
def stand(s,img,x,ground,flip=False):
    if flip: img=img.transpose(Image.FLIP_LEFT_RIGHT)
    put(s,img,x,ground-bottom(img)+2)
def prop(s,i,x,ground): stand(s,t(i),x,ground)
def tag(s,text,cx,y,bg=(16,22,31,215),fg=(255,255,255,255)):
    l,tp,r,b=FONT.getbbox(text); w=r-l+6; h=12
    lay=Image.new('RGBA',s.size,(0,0,0,0)); d=ImageDraw.Draw(lay); d.fontmode='1'
    x=int(cx-w/2); d.rectangle((x,y,x+w-1,y+h-1),fill=bg)
    d.text((x+3-l,y+1),text,font=FONT,fill=fg)
    s.alpha_composite(lay)
def bubble(s,text,cx,bottom_y):
    """말풍선: 꼬리 끝이 (cx, bottom_y)에 닿는다. 글자는 갈무리9 1배."""
    l,tp,r,b=FONT.getbbox(text); w=r-l+8; h=13
    lay=Image.new('RGBA',s.size,(0,0,0,0)); d=ImageDraw.Draw(lay); d.fontmode='1'
    x=int(cx-w/2); y=bottom_y-h-3
    edge=(43,49,66,255); fill=(255,255,255,255)
    d.rectangle((x+1,y,x+w-2,y+h-1),fill=fill); d.rectangle((x,y+1,x+w-1,y+h-2),fill=fill)
    d.line((x+1,y-1,x+w-2,y-1),fill=edge); d.line((x+1,y+h,x+w-2,y+h),fill=edge)
    d.line((x-1,y+1,x-1,y+h-2),fill=edge); d.line((x+w,y+1,x+w,y+h-2),fill=edge)
    d.point([(x,y),(x+w-1,y),(x,y+h-1),(x+w-1,y+h-1)],fill=edge)
    d.polygon([(cx-2,y+h),(cx+2,y+h),(cx,y+h+2)],fill=fill); d.point([(cx-3,y+h),(cx+3,y+h)],fill=edge)
    d.line((cx-2,y+h+1,cx-1,y+h+2),fill=edge); d.line((cx+2,y+h+1,cx+1,y+h+2),fill=edge); d.point((cx,y+h+3),fill=edge)
    d.text((x+4-l,y+1),text,font=FONT,fill=(27,39,53,255))
    s.alpha_composite(lay)
OUT='scenes/'
def home_island(s, gy=92):
    put(s, island(3,1), 6, 44); put(s, island(3,1), 160, 34); put(s, island(9,2), 16, gy)
    prop(s,126,24,gy); prop(s,84,44,gy); prop(s,105,62,gy); prop(s,106,80,gy)
    prop(s,150,150,gy); put(s,t(130),150,gy-36+2); prop(s,111,170,gy); prop(s,124,128,gy)
G=92
# 1 집
s=base(); home_island(s); stand(s,spr('ranger'),104,G); s.save(OUT+'s_home.png')
# 2 처음 시작: 세 직업
s=base(); put(s, island(3,1), 8, 50); put(s, island(4,1), 152, 36); put(s, island(7,2), 52, G)
prop(s,126,58,G); prop(s,124,140,G); prop(s,128,156,G)
stand(s,spr('knight'),78,G); stand(s,spr('ranger'),98,G); stand(s,spr('wizard'),118,G); s.save(OUT+'s_start.png')
# 3 탐사 (비구름 지대, 사냥꾼과 게)
s=base(sat=0.55,dark=0.85); put(s, island(3,1,'snow'), 152, 40); put(s, island(7,2,'snow'), 30, G)
prop(s,126,46,G); prop(s,126,136,G)
stand(s,spr('ranger'),76,G); stand(s,spr('crab'),104,G,flip=True); bubble(s,'게다!',84,G-18); s.save(OUT+'s_explore.png')
# 4 보스전 (폭풍의 벽)
s=base(tint=(88,70,150,120),dark=0.8); put(s, island(9,2), 10, G)
prop(s,126,18,G); prop(s,126,160,G)
stand(s,spr('wizard'),34,G); stand(s,spr('ranger'),54,G); stand(s,spr('knight'),82,G)
boss=spr('bat'); boss=boss.resize((boss.width*2,boss.height*2),Image.NEAREST); put(s,boss,118,46)
bubble(s,'치유의 빛!',42,G-18); bubble(s,'내 뒤로!',90,G-30)
s.save(OUT+'s_battle.png')
# 5 결과 (폭풍이 걷힌 하늘)
s=base(); put(s, island(9,2), 10, G); prop(s,126,18,G); prop(s,111,150,G); prop(s,126,168,G)
stand(s,spr('wizard'),54,G); stand(s,spr('ranger'),76,G); stand(s,spr('knight'),98,G)
feather=Image.open('dl/496_RPG_icons/I_Feather01.png').convert('RGBA').resize((17,17),Image.NEAREST); put(s,feather,124,68)
s.save(OUT+'s_result.png')
# 6 섬 손님 (이름표 포함)
s=base(); home_island(s)
for name,sp,x,fl,y,host in (('노을','ranger',60,False,62,True),('바위','knight',90,False,62,False),('레아','wizard',120,False,62,False),('솔','ranger',140,True,48,False)):
    stand(s,spr(sp),x,G,fl)
    if host: tag(s,name,x+8,y,bg=(46,110,190,235))
    else: tag(s,name,x+8,y)
s.save(OUT+'s_guests.png')
# 7 프로필 (마법사)
s=base(); home_island(s); stand(s,spr('wizard'),104,G); s.save(OUT+'s_profile.png')
# 8 길드 섬 (하늘등대): 넓은 섬, 깃발 둘, 길드원 여럿
s=base(); put(s, island(3,1), 4, 40); put(s, island(10,2), 7, G)
prop(s,111,12,G); prop(s,111,172,G); put(s,t(130),150,G-36+2); prop(s,150,150,G); prop(s,84,26,G)
for sp,x,fl in (('knight',44,False),('ranger',62,False),('wizard',80,False),('knight',98,True),('ranger',114,True),('wizard',132,True)):
    stand(s,spr(sp),x,G,fl)
tag(s,'하늘등대',97,30,bg=(46,110,190,235))
s.save(OUT+'s_guild.png')
sheet=Image.new('RGBA',(390*4+30,260*2+10),(16,22,31,255))
for i,n in enumerate(('s_home','s_start','s_explore','s_battle','s_result','s_guests','s_profile')):
    im=Image.open(OUT+n+'.png').resize((390,260),Image.NEAREST); sheet.paste(im,((i%4)*400,(i//4)*270))
sheet.save(OUT+'compare3.png')
