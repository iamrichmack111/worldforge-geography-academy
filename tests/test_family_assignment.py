"""Integration test: parent-owned homework must never leak to unrelated accounts."""
import http.cookiejar, json, os, sys, tempfile, threading, unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import build_opener, HTTPCookieProcessor, Request
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
class FamilyAssignments(unittest.TestCase):
 def test_end_to_end(self):
  with tempfile.TemporaryDirectory() as tmp:
   old=server.DB;server.DB=Path(tmp)/'school.sqlite3';server.setup()
   httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start();url=f'http://127.0.0.1:{httpd.server_address[1]}/api/'
   def client():return build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
   def api(c,path,data=None):
    h={'X-WorldForge-Request':'1'}
    if data is not None:h['Content-Type']='application/json'
    try:
     with c.open(Request(url+path,data=None if data is None else json.dumps(data).encode(),headers=h)) as r:return r.status,json.load(r)
    except HTTPError as e:return e.code,json.load(e)
   def register(c,name,role):
    self.assertEqual(api(c,'signup',dict(username=name,email=name+'@test.local',password='password123',role=role))[0],201)
    self.assertEqual(api(c,'login',dict(username=name,password='password123'))[0],200)
   try:
    parent,child,stranger=client(),client(),client()
    register(parent,'guardian001','parent');register(child,'pupil001','student');register(stranger,'otherparent','parent')
    studentid=api(child,'me')[1]['user']['id'];payload=dict(student_id=studentid,title='Analyze coastal erosion',instructions='Describe three ways waves can reshape a coastline.',topic='coasts',due_at='2027-01-20')
    self.assertEqual(api(parent,'parent-assignment',payload)[0],403)
    code=api(child,'link-code',{})[1]['code'];self.assertEqual(api(parent,'link-child',{'code':code})[0],200)
    self.assertEqual(api(parent,'parent-assignment',payload)[0],201)
    items=api(child,'assignments')[1]['assignments'];target=next(x for x in items if x['title']==payload['title'])
    self.assertEqual(api(stranger,'children')[1]['children'],[])
    self.assertEqual(api(stranger,'parent-assignment',payload)[0],403)
    self.assertEqual(api(child,'submit',dict(assignment_id=target['id'],answer='Waves erode cliffs, move sediment and build beaches.'))[0],200)
    parent_rows=api(parent,'children')[1]['children'];entry=next(x for x in parent_rows[0]['assignments'] if x['assignment_id']==target['id'])
    self.assertEqual(api(stranger,'parent-grade',dict(submission_id=entry['submission_id'],grade=100))[0],403)
    self.assertEqual(api(parent,'parent-grade',dict(submission_id=entry['submission_id'],grade=87,feedback='Good examples'))[0],200)
    refreshed=next(x for x in api(child,'assignments')[1]['assignments'] if x['id']==target['id']);self.assertEqual(refreshed['grade'],87)
    self.assertEqual(api(parent,'unlink-child',{'student_id':studentid})[0],200)
    self.assertEqual(api(parent,'parent-grade',dict(submission_id=entry['submission_id'],grade=0))[0],403)
   finally:
    httpd.shutdown();httpd.server_close();server.DB=old
if __name__=='__main__':unittest.main()
