import sys
from PIL import Image, ImageDraw
from ohlalive_kit import *
S=SCALE
VILLES=["MARSEILLE","NICE","CANNES","SAINT-TROPEZ","ANTIBES","MONACO","TOULON","AIX-EN-PROVENCE","MONTPELLIER","SAINT-RAPHAËL","FRÉJUS"]
def story(scheme):
    W,H=1080*S,1920*S; sc=SCHEMES[scheme]; cx=W//2
    im=Image.new("RGB",(W,H),sc["bg"]); d=ImageDraw.Draw(im)
    logo=lockup(scheme,560*S); paste_rgba(im,logo,cx-logo.width//2,int(270*S))
    y=int(270*S)+logo.height+int(70*S)
    def tr(text,font,col,track=0,gap=0):
        nonlocal y
        b=d.textbbox((0,0),text,font=font); h=b[3]-b[1]
        if track: draw_tracked(d,y-b[1],text,font,col,tracking=track,cx=cx)
        else: draw_centered(d,y-b[1],text,font,col,cx)
        y+=h+int(gap*S)
    tr("OHLALIVE ARRIVE DANS LE SUD",jost("SemiBold",31*S),sc["accent"],int(5*S),50)
    tr("Vous avez un",playfair("Bold",112*S),sc["text"],0,10)
    tr("dressing à vider ?",playfair("Bold",112*S),sc["text"],0,50)
    d.rectangle([cx-45*S,y,cx+45*S,y+3*S],fill=sc["accent"]); y+=int(55*S)
    tr("Contactez-nous.",playfair_italic("Medium Italic",100*S),sc["text"],0,14)
    tr("On s'occupe de tout.",playfair_italic("Medium Italic",100*S),sc["accent"],0,34)
    tr("ON TRIE  ·  ON VEND EN LIVE  ·  VOUS ÊTES PAYÉE",jost("SemiBold",27*S),sc["text"],int(4*S),56)
    tr("06 59 64 32 57",playfair("Medium",104*S),sc["accent"],0,16)
    tr("WhatsApp ou DM  ·  @ohlaliveparis",playfair_italic("Medium Italic",40*S),sc["text"],0,0)
    # villes en bas (zone sûre)
    f=jost("Medium",24*S); l1="  ·  ".join(VILLES[:4]); l2="  ·  ".join(VILLES[4:8]); l3="  ·  ".join(VILLES[8:])
    yy=int(1920*S)-int(270*S)-int(130*S)
    for l in (l1,l2,l3):
        b=d.textbbox((0,0),l,font=f); draw_tracked(d,yy-b[1],l,f,sc["text"],tracking=int(2*S),cx=cx); yy+=int(46*S)
    return finish(im,1080,1920)
for s in ("mimosa","framboise"):
    story(s).save(f"sud/STORY_sud_{s}.png")
