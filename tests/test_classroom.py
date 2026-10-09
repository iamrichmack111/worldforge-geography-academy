"""Runs with stdlib unittest or pytest. Tests every classroom API workflow."""
import http.cookiejar
import json
import os
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import build_opener, HTTPCookieProcessor, Request

import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server

class ClassroomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        server.DB=Path(cls.tmp.name)/'test.sqlite3'
        os.environ['WORLDFORGE_TEACHER_CODE']='teacher-test-42'
        server.setup()
        cls.httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        cls.thread=threading.Thread(target=cls.httpd.serve_forever,daemon=True)
        cls.thread.start()
        cls.url='http://127.0.0.1:'+str(cls.httpd.server_address[1])
    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown();cls.httpd.server_close();cls.tmp.cleanup()
        os.environ.pop('WORLDFORGE_TEACHER_CODE',None)
    def setUp(self): self.client=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    def call(self,path,data=None,client=None):
        headers={'X-WorldForge-Request':'1'}
        if data is not None: headers['Content-Type']='application/json'
        req=Request(self.url+'/api/'+path, data=None if data is None else json.dumps(data).encode(),headers=headers)
        try:
            with (client or self.client).open(req) as r: return r.status,json.load(r)
        except HTTPError as e: return e.code,json.load(e)
    def signup(self,name,role='student',code=None):
        return self.call('signup',{'username':name,'email':name+'@example.com','password':'securepass123','role':role,'teacher_code':code})
    def login(self,name):return self.call('login',{'username':name,'password':'securepass123'})
    def test_01_signup_login_logout(self):
        self.assertEqual(self.signup('alice')[0],201)
        self.assertEqual(self.signup('alice')[0],409)
        self.assertEqual(self.call('me')[1]['user'],None)
        self.assertEqual(self.login('alice')[0],200)
        self.assertEqual(self.call('me')[1]['user']['username'],'alice')
        self.assertEqual(self.call('logout',{})[0],200)
        self.assertIsNone(self.call('me')[1]['user'])
    def test_02_student_submissions_saved_and_updated(self):
        self.signup('bobby');self.login('bobby')
        status,rows=self.call('assignments');self.assertEqual(status,200);self.assertGreater(len(rows['assignments']),0)
        first=rows['assignments'][0]['id']
        self.assertEqual(self.call('submit',{'assignment_id':first,'answer':'Water flows from higher ridges toward valleys.'})[0],200)
        self.assertEqual(self.call('submit',{'assignment_id':first,'answer':'Mountain ridges divide drainage basins.'})[0],200)
        updated=self.call('assignments')[1]['assignments'][0]
        self.assertEqual(updated['answer'],'Mountain ridges divide drainage basins.')
        self.assertIsNotNone(updated['submitted_at'])
        self.assertEqual(self.call('assignment',{'title':'Secret','instructions':'Teacher-only work','topic':'geo','due_at':'2026-12-01'})[0],403)
    def test_03_teacher_invite_create_grade(self):
        self.assertEqual(self.signup('badteach','teacher','wrong')[0],403)
        self.assertEqual(self.signup('geoteacher','teacher','teacher-test-42')[0],201)
        self.login('geoteacher')
        self.assertEqual(self.call('assignment',{'title':'Locate a valley','instructions':'Explain how you found the lowest terrain.','topic':'topography','due_at':'2027-02-10'})[0],201)
        rows=self.call('assignments')[1]['assignments']
        self.assertTrue(any(a['title']=='Locate a valley' for a in rows))
        submitted=self.call('submissions')[1]['submissions']
        self.assertGreaterEqual(len(submitted),1)
        sid=submitted[0]['id']
        self.assertEqual(self.call('grade',{'submission_id':sid,'grade':91,'feedback':'Good use of terms.'})[0],200)
        self.assertEqual(self.call('grade',{'submission_id':sid,'grade':101,'feedback':'Wrong'})[0],400)
    def test_04_protected_and_input_validation(self):
        self.assertEqual(self.call('assignments')[0],401)
        self.assertEqual(self.signup('short','student')[0],201)
        self.assertEqual(self.call('login',{'username':'short','password':'wrong'})[0],401)
        self.assertEqual(self.call('signup',{'username':'x','email':'bad','password':'short','role':'student'})[0],400)
    def test_06_parent_links_permissions_announcements_goals(self):
        self.assertEqual(self.signup('parentmary','parent')[0],201)
        self.login('parentmary')
        self.assertEqual(self.call('children')[1]['children'],[])
        self.assertEqual(self.call('assignments')[0],403)
        self.assertEqual(self.call('grade',{'submission_id':1,'grade':100})[0],403)
        self.assertEqual(self.call('link-code',{})[0],403)
        self.assertEqual(self.call('link-child',{'code':'invalidcode001'})[0],400)
        parent_client=self.client
        self.client=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.assertEqual(self.signup('childcora')[0],201)
        self.login('childcora')
        self.assertEqual(self.call('goal',{'title':'Learn continental divides'})[0],201)
        goal=self.call('goals')[1]['goals'][0]
        self.assertEqual(self.call('toggle-goal',{'goal_id':goal['id']})[0],200)
        self.assertEqual(self.call('announcements')[0],200)
        self.assertEqual(self.call('announcement',{'title':'News today','body':'Review your maps carefully'})[0],403)
        code=self.call('link-code',{})[1]['code']
        self.assertEqual(self.call('link-child',{'code':code})[0],403)
        self.assertEqual(self.call('children')[0],403)
        self.assertEqual(self.call('link-child',{'code':code},parent_client)[0],200)
        self.assertEqual(self.call('link-child',{'code':code},parent_client)[0],400)
        children=self.call('children',client=parent_client)[1]['children']
        self.assertEqual(len(children),1)
        self.assertEqual(children[0]['username'],'childcora')
        self.assertEqual(children[0]['goals'][0]['done'],1)
        self.assertEqual(self.call('unlink-child',{'student_id':children[0]['id']},parent_client)[0],200)
        self.assertEqual(self.call('children',client=parent_client)[1]['children'],[])
        self.client=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.login('geoteacher')
        self.assertEqual(self.call('announcement',{'title':'Field trip','body':'Study the river basin next week'})[0],201)
        self.assertEqual(self.call('announcements')[1]['announcements'][0]['title'],'Field trip')
    def test_05_static_files(self):
        for name in ('classroom.html','classroom.js','classroom.css','geography3d.html'):
            with self.client.open(self.url+'/'+name) as response:self.assertEqual(response.status,200)
if __name__=='__main__':unittest.main()
