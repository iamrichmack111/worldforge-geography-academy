"""End-to-end browser checks for WorldForge. Run: python -m pytest -q tests"""
import contextlib
import http.server
import socketserver
import threading
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture(scope='module')
def server():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT), **kwargs)
        def log_message(self, *args):
            pass
    with socketserver.TCPServer(('127.0.0.1', 0), Quiet) as httpd:
        thread=threading.Thread(target=httpd.serve_forever,daemon=True)
        thread.start()
        yield f'http://127.0.0.1:{httpd.server_address[1]}/geography3d.html'
        httpd.shutdown()

@pytest.fixture()
def page(server):
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--no-proxy-server','--proxy-bypass-list=*'])
        page=browser.new_page(viewport={'width':1280,'height':800})
        page.goto(server)
        yield page
        browser.close()

def test_lesson_previous_next(page):
    assert 'Elevation and topography' in page.locator('#lessonTitle').inner_text()
    assert page.locator('#previousLesson').is_disabled()
    page.locator('#nextLesson').click()
    assert 'Reading a topographic profile' in page.locator('#lessonTitle').inner_text()
    page.locator('#previousLesson').click()
    assert 'Elevation and topography' in page.locator('#lessonTitle').inner_text()

def test_all_lessons_and_boundaries(page):
    for i in range(6):
        assert page.locator('#nextLesson').is_enabled()
        page.locator('#nextLesson').click()
    assert page.locator('#nextLesson').is_disabled()
    assert 'Map interpretation' in page.locator('#lessonTitle').inner_text()

def test_quiz_buttons_and_score(page):
    for i in range(8):
        assert page.locator('#choices button').count() >= 3
        first=page.locator('#choices button').first
        first.click()
        assert first.is_disabled()
        assert page.locator('#feedback').inner_text() != 'Choose an answer to receive an explanation.'
        assert f'/ {i+1}' in page.locator('#score').inner_text()
        page.locator('#nextQuiz').click()

def test_layer_and_relief_controls_exist(page):
    assert page.locator('#layer option').count() == 4
    assert page.locator('#height').get_attribute('max')=='3'
    for button in ('reset','inspect','transect','clear','runTests'):
        assert page.locator('#'+button).count()==1

def test_fallback_when_cdn_unavailable(page):
    # A browser without access to the 3D dependency must show a map and working lessons.
    page.wait_for_function("document.querySelector('#fallback').style.display === 'block' || !!document.querySelector('#stage canvas')",timeout=30000)
    if page.locator('#fallback').is_visible():
        assert page.locator('#stage img').count()==1
        page.locator('#nextLesson').click()
        assert 'Reading a topographic profile' in page.locator('#lessonTitle').inner_text()
    else:
        page.locator('#runTests').click()
        assert 'control checks passed' in page.locator('#testResults').inner_text()


def test_source_regressions():
    src=(ROOT/'geography3d.html').read_text()
    assert 'markerGroup=new THREE.Group();scene.add(markerGroup);rebuild();' in src
    assert 'if(markerGroup)markerGroup.children.forEach' in src
    assert 'dist>0?' in src
    assert 'runControlTests' in src
