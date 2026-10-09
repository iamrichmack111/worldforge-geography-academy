import importlib.util, os, tempfile, unittest
from datetime import timedelta
from pathlib import Path
spec=importlib.util.spec_from_file_location('wf_v11_server',Path(__file__).resolve().parents[1]/'server.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class DailyTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();m.DB=Path(self.t.name)/'temp.sqlite3';m.setup()
  with m.db() as con:
   con.execute("INSERT INTO users(username,email,pass_hash,role,created_at) VALUES('kid','kid@example.test','x','student',?)",(m.iso(m.utcnow()),))
   self.user={'id':con.execute("SELECT id FROM users WHERE username='kid'").fetchone()[0],'role':'student'}
 def tearDown(self):self.t.cleanup()
 def test_grows_each_day_and_caps(self):
  with m.db() as con:
   first=m.daily_data(self.user,con);self.assertEqual(first['total'],5)
   con.execute('UPDATE users SET created_at=? WHERE id=?',(m.iso(m.utcnow()-timedelta(days=5)),self.user['id']))
   later=m.daily_data(self.user,con);self.assertEqual(later['total'],10)
   con.execute('UPDATE users SET created_at=? WHERE id=?',(m.iso(m.utcnow()-timedelta(days=90)),self.user['id']))
   capped=m.daily_data(self.user,con);self.assertEqual(capped['total'],20)
 def test_student_day_is_stable(self):
  with m.db() as con:
   a=m.daily_data(self.user,con);b=m.daily_data(self.user,con)
   self.assertEqual(a['ids'],b['ids'])
   con.execute('INSERT INTO daily_challenges VALUES(?,?,?,?,?,?)',(self.user['id'],a['date'],a['day'],3,5,m.iso(m.utcnow())))
   done=m.daily_data(self.user,con)
   self.assertEqual(done['completed']['score'],3);self.assertEqual(done['streak'],1)
if __name__=='__main__':unittest.main()
