import re
BL=['133d7264c31aa4599a9d5649e4ced252','614787881a2509a5dfe15e88a8a79054','04ce3ab8c74bdabe38e958a86133d679','966df3d5d1818e3f0e6734181bcde540','3de277ad24e1814fd99bdad7e3830303']
def find(t):
    h=min(t.find(b) for b in BL if t.find(b)>=0)
    s=t.rfind('<',0,h); name=re.match(r'<(\w+)',t[s:]).group(1)
    i=s; depth=0
    for m in re.finditer(r'<(/?)'+name+r'\b',t[s:]):
        depth+= -1 if m.group(1) else 1
        if depth==0:
            e=t.index('>',s+m.start())+1; return s,e
