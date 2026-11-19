#!/usr/bin/env python3
"""Miniatura 9:16 + 3:4 (contenido entre y 240-1680). Salón desenfocado detrás, EL sofá nítido con foco de luz,
sello VAGO con textura y titular «¿Y SI TE PONES A TRABAJAR?» con subrayado de rotulador."""
import os, sys, subprocess
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, B)
import _sets
def salon(sid):
    return (_sets.salon(sid).replace('stroke-dashoffset="1"', 'stroke-dashoffset="0"').replace('HOGAR, DULCE HOGAR', ''))
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1920px;overflow:hidden;background:#06040c;font-family:Inter}}
#fondo,#nitido{{position:absolute;inset:0;transform-origin:540px 1400px}}
#fondo{{transform:scale(1.12);filter:blur(7px) brightness(.55) saturate(1.2)}}
#nitido{{transform:scale(1.12);-webkit-mask-image:linear-gradient(180deg,transparent 54%,#000 61%);filter:saturate(1.15)}}
#foco{{position:absolute;inset:0;background:radial-gradient(ellipse 620px 300px at 50% 1390px,rgba(255,214,140,.32),transparent 70%)}}
#tv{{position:absolute;inset:0;background:radial-gradient(ellipse 700px 500px at 0% 1500px,rgba(70,150,255,.35),transparent 70%),radial-gradient(ellipse 600px 500px at 100% 1300px,rgba(255,170,80,.25),transparent 70%);mix-blend-mode:screen}}
#osc{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(6,4,12,.95) 0%,rgba(6,4,12,.7) 30%,rgba(6,4,12,0) 52%,rgba(6,4,12,0) 80%,rgba(6,4,12,.9) 100%)}}
#vin{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 58%,transparent 45%,rgba(0,0,0,.7) 100%)}}
#grano{{position:absolute;inset:0;background:url(../assets/grano.png);opacity:.08;mix-blend-mode:overlay}}
.c{{position:absolute;left:0;right:0;text-align:center}}
#t1{{top:318px;font:900 112px/1 Inter;letter-spacing:-4px;color:#fff;text-shadow:0 8px 30px rgba(0,0,0,.9)}}
#t2{{top:446px}} #t2 span{{position:relative;white-space:nowrap;display:inline-block;font:900 132px/1 Inter;letter-spacing:-6px;color:#111;padding:6px 34px 14px;transform:rotate(-2.5deg)}}
#t2 span:before{{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,#ffe066,#ffc531);border-radius:18px;box-shadow:0 18px 50px rgba(0,0,0,.6),0 0 0 6px rgba(0,0,0,.25)}}
#sello{{top:930px}} #sello span{{position:relative;display:inline-block;font:900 176px/1 Inter;letter-spacing:10px;color:#ff3346;padding:22px 46px 14px;border:16px solid #ff3346;border-radius:24px;transform:rotate(-8deg);
  background:rgba(14,3,8,.86);box-shadow:0 30px 70px rgba(0,0,0,.75),0 0 50px rgba(255,51,70,.45);
  -webkit-mask-image:repeating-radial-gradient(circle at 30% 40%,#000 0 3px,rgba(0,0,0,.82) 3px 5px),linear-gradient(#000,#000);-webkit-mask-composite:source-over}}
#sello small{{position:absolute;left:0;right:0;bottom:-58px;font:800 30px Inter;letter-spacing:12px;color:#ff8a95}}
#borde{{position:absolute;inset:0;box-shadow:inset 0 0 0 0 transparent}}
</style></head><body>
<div id="fondo">{salon("f")}</div><div id="nitido">{salon("n")}</div>
<div id="foco"></div><div id="tv"></div><div id="osc"></div><div id="vin"></div><div id="grano"></div>
<div class="c" id="t1">¿Y SI TE PONES</div>
<div class="c" id="t2"><span>A TRABAJAR?</span></div>
<div class="c" id="sello"><span>VAGO</span></div>
</body></html>'''
html = html.replace('<svg class="set"', '<svg class="set" style="position:absolute;inset:0"')
open(os.path.join(B, "miniatura", "mini.html"), "w", encoding="utf-8").write(html)
js = f'''const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
await p.goto('file://{B}/miniatura/mini.html');await p.waitForTimeout(800);
await p.screenshot({{path:'{B}/miniatura/miniatura_9x16.png'}});await p.screenshot({{path:'{B}/miniatura/miniatura_tiktok_3x4.png',clip:{{x:0,y:240,width:1080,height:1440}}}});await b.close()}})();'''
subprocess.check_call(["node", "-e", js]); print("ok")
