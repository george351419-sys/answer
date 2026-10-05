import unittest
from scripts.build import apply_rows, HEADERS, seconds, read_rows, ROOT
class ImportTests(unittest.TestCase):
 def rows(self,*rows): return [(1,HEADERS)]+[(i+2,r) for i,r in enumerate(rows)]
 def test_template(self):
  result=apply_rows({},self.rows(['新增','测试','数学实景题','我是数学王子','我爱数学','3','1']))
  self.assertEqual(result['测试']['delay2'],60)
 def test_optional_and_defaults(self):
  result=apply_rows({},self.rows(['新增','A','题目','提示','','','']))['A']
  self.assertEqual(result['delay1'],180); self.assertEqual(result['hint2'],'')
 def test_update_delete(self):
  catalog=apply_rows({},self.rows(['新增','A','题目','提示','','','']))
  apply_rows(catalog,self.rows(['新增','A','新题目','新提示','二','0.5','1']))
  self.assertEqual(catalog['A']['delay1'],30)
  apply_rows(catalog,self.rows(['删除','A','新题目','新提示','','','']))
  self.assertEqual(catalog,{})
 def test_invalid(self):
  for value in ['-1','0','nan','inf','三分钟']:
   with self.assertRaises(ValueError): seconds(value)
  for key in ['../x','a/b','..','assets','a?b']:
   with self.assertRaises(ValueError): apply_rows({},self.rows(['新增',key,'题','提示','','','']))
 def test_duplicate_and_required(self):
  row=['新增','A','题','提示','','','']
  with self.assertRaises(ValueError): apply_rows({},self.rows(row,row))
  with self.assertRaises(ValueError): apply_rows({},self.rows(['新增','A','','提示','','','']))
if __name__=='__main__':unittest.main()
