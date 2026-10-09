"""HTTP regression: quizzes are server-scored and private to a student's family."""
import http.cookiejar, json, sys, tempfile, threading, unittest
from pathlib import Path
from urllib.request import build_opener, HTTPCookieProcessor, Request
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server

class PracticeTests(unittest.TestCase):
    def test_scoring_validation_and_parent_visibility(self):
        with tempfile.TemporaryDirectory() as root:
            prior=server.DB
            server.DB=Path(root)/'school.sqlite3'; server.setup()
            httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
            worker=threading.Thread(target=httpd.serve_forever,daemon=True);worker.start()
            base=f'http://127.0.0.1:{httpd.server_address[1]}/api/'
            def client():return build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
            def call(c,path,data=None):
                headers={'X-WorldForge-Request':'1'}
                if data is not None:headers['Content-Type']='application/json'
                try:
                    with c.open(Request(base+path,data=None if data is None else json.dumps(data).encode(),headers=headers)) as r:return r.status,json.load(r)
                except HTTPError as e:return e.code,json.load(e)
            def user(c,name,role):
                self.assertEqual(call(c,'signup',{'username':name,'email':name+'@test.local','password':'password123','role':role})[0],201)
                self.assertEqual(call(c,'login',{'username':name,'password':'password123'})[0],200)
            try:
                kid,guardian,other=client(),client(),client()
                user(kid,'quizkid','student'); user(guardian,'quizparent','parent'); user(other,'anotherparent','parent')
                status,bank=call(kid,'practice');self.assertEqual(status,200)
                rows=[q for q in bank['questions'] if q['topic']=='landforms']
                self.assertEqual(len(rows),5)
                self.assertNotIn('correct_option',rows[0])
                self.assertEqual(call(kid,'practice-submit',{'topic':'landforms','answers':{str(rows[0]['id']):1}})[0],400)
                self.assertEqual(call(guardian,'practice-submit',{'topic':'landforms','answers':{str(q['id']):0 for q in rows}})[0],403)
                self.assertEqual(call(kid,'practice-submit',{'topic':'landforms','answers':{str(q['id']):True for q in rows}})[0],400)
                status,result=call(kid,'practice-submit',{'topic':'landforms','answers':{str(q['id']): [1,0,0,1,0][index] for index,q in enumerate(rows)}})
                self.assertEqual(status,200);self.assertEqual(result['score'],5);self.assertEqual(result['total'],5)
                self.assertEqual(call(kid,'practice')[1]['history'][0]['score'],5)
                self.assertEqual(call(guardian,'children')[1]['children'],[])
                self.assertEqual(call(other,'children')[1]['children'],[])
                code=call(kid,'link-code',{})[1]['code'];self.assertEqual(call(guardian,'link-child',{'code':code})[0],200)
                self.assertEqual(call(guardian,'children')[1]['children'][0]['practice'][0]['score'],5)
                self.assertEqual(call(guardian,'unlink-child',{'student_id':call(kid,'me')[1]['user']['id']})[0],200)
                self.assertEqual(call(guardian,'children')[1]['children'],[])
            finally:
                httpd.shutdown();httpd.server_close();server.DB=prior
if __name__=='__main__':unittest.main()
