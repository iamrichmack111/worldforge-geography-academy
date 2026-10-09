#!/usr/bin/env python3
"""Capture actual pages, not simulated screenshots."""
import os, sys, pathlib, json
from playwright.sync_api import sync_playwright
base=os.getenv('WORLDFORGE_DEMO_URL','http://127.0.0.1:8032').rstrip('/')
out=pathlib.Path('media/screenshots');out.mkdir(parents=True,exist_ok=True)
urls=[('login','/classroom.html?v=13'),('mountains','/landform-quest.html'),('earth-3d','/geography3d.html')]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':900}, device_scale_factor=1)
    for name,path in urls:
        print(f'Capturing {name}: {base+path}',flush=True)
        page.goto(base+path,wait_until='domcontentloaded',timeout=30000)
        page.wait_for_timeout(1600)
        page.screenshot(path=str(out/f'{name}.png'),full_page=False,animations='disabled')
        assert (out/f'{name}.png').stat().st_size>5000
    browser.close()
print('Screenshots created:',*(str(x) for x in sorted(out.glob('*.png'))))
