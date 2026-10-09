import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class EarthQuestTest(unittest.TestCase):
 def test_three_units_and_spots(self):
  s=(ROOT/'landform-data.js').read_text()
  m=re.search(r'window.WF_QUEST_DATA=(.*?);\n',s)
  data=json.loads(m.group(1))
  self.assertEqual(set(data),{'earth','mountains','terrain'})
  for k,items in data.items():
   self.assertEqual(len(items),12,k)
   for title,q,opts,right,explanation in items:
    self.assertTrue(title and q and explanation)
    self.assertTrue(0<=right<len(opts))
    self.assertEqual(len(opts),3)
 def test_page_has_interactive_hooks(self):
  page=(ROOT/'landform-quest.html').read_text()
  self.assertIn('landform-quest.js',page)
  self.assertIn('landform-data.js',page)
  for k in ('mountains','terrain','earth'):
   self.assertIn('data-unit="'+k+'"',page)
