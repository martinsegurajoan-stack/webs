#!/usr/bin/env python3
"""Miniatura 9:16 + 3:4 (contenido entre y 240-1680): el salón con EL sofá, sello VAGO, titular y gancho GTA."""
import os, sys, subprocess
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, B)
import _sets
svg = _sets.salon("m").replace('stroke-dashoffset="1"', 'stroke-dashoffset="0"').replace('visibility:hidden', '')
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1920px;overflow:hidden;background:#000;font-family:Inter}}
.set{{position:absolute;inset:0;transform:scale(1.08);transform-origin:540px 1400px}}
#osc{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,3,12,.92) 0%,rgba(5,3,12,.55) 38%,rgba(5,3,12,0) 55%,rgba(5,3,12,.15) 80%,rgba(5,3,12,.85) 100%)}}
#vin{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 60%,transparent 50%,rgba(0,0,0,.65) 100%)}}
.c{{position:absolute;left:0;right:0;text-align:center;color:#fff}}
#pill{{top:300px}} #pill span{{display:inline-block;font:900 38px Inter;letter-spacing:4px;color:#111;background:#ffd166;padding:12px 28px;border-radius:14px;transform:rotate(-2deg);box-shadow:0 10px 30px rgba(0,0,0,.5)}}
#tit{{top:390px;font:900 128px/0.95 Inter;letter-spacing:-5px;text-shadow:0 10px 40px rgba(0,0,0,.9)}} #tit b{{color:#3ddc84}}
#vago{{top:820px}} #vago span{{display:inline-block;font:900 210px Inter;letter-spacing:6px;color:#ff3b4e;padding:4px 50px;border:18px solid #ff3b4e;border-radius:28px;transform:rotate(-9deg);
  background:rgba(20,5,10,.85);box-shadow:0 0 60px rgba(255,59,78,.55),inset 0 0 40px rgba(255,59,78,.3);text-shadow:0 0 30px rgba(255,59,78,.6)}}
#flecha{{top:1210px;left:120px;right:auto;font:900 40px Inter;color:#111;background:#fff;padding:12px 24px;border-radius:14px;transform:rotate(-4deg)}}
#gta{{top:1480px}} #gta div{{display:inline-block;padding:18px 40px;border-radius:24px;background:linear-gradient(135deg,#ff2e88,#7c3aed);box-shadow:0 0 70px rgba(255,46,136,.7);transform:rotate(3deg)}}
#gta small{{display:block;font:800 30px Inter;letter-spacing:6px}} #gta b{{font:italic 900 96px/1 Inter;letter-spacing:-2px;text-shadow:4px 4px 0 #000}}
</style></head><body>{svg}<div id="osc"></div><div id="vin"></div>
<div class="c" id="pill"><span>25 AÑOS EN EL SOFÁ 🛋️</span></div>
<div class="c" id="tit">¿Y SI TE PONES<br>A <b>TRABAJAR?</b></div>
<div class="c" id="vago"><span>VAGO</span></div>
<div class="c" id="flecha">↓ TU HUECO</div>
<div class="c" id="gta"><div><small>…Y ENTONCES SALE</small><b>GTA VI</b></div></div>
</body></html>'''
open(os.path.join(B, "miniatura", "mini.html"), "w", encoding="utf-8").write(html)
js = f'''const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
await p.goto('file://{B}/miniatura/mini.html');await p.waitForTimeout(700);
await p.screenshot({{path:'{B}/miniatura/miniatura_9x16.png'}});await p.screenshot({{path:'{B}/miniatura/miniatura_tiktok_3x4.png',clip:{{x:0,y:240,width:1080,height:1440}}}});await b.close()}})();'''
subprocess.check_call(["node", "-e", js]); print("ok")
