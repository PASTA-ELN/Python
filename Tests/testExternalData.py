#!/usr/bin/python3
"""
TEST IF EXTERNAL DATA CAN BE READ,...
"""
import os, shutil, traceback, sys, time
import warnings
import unittest
sys.path.append('/home/sbrinckm/FZJ/SourceCode/Micromechanics/src')  #allow debugging in vscode which strips the python-path
sys.path.append('/home/sbrinckm/FZJ/JamDB/Python')
from backend import JamDB

class TestStringMethods(unittest.TestCase):
  def test_main(self):
    ### MAIN ###
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
    warnings.filterwarnings('ignore', category=ImportWarning)
    warnings.filterwarnings('ignore', module='js2py')

    databaseName = 'temporary_test0'
    self.dirName      = os.path.expanduser('~')+os.sep+databaseName
    if os.path.exists(self.dirName): shutil.rmtree(self.dirName)
    os.makedirs(self.dirName)
    self.be = JamDB(databaseName)
    self.be.exit(deleteDB=True)
    self.be = JamDB(databaseName)

    try:
      ### create some project and move into it
      self.be.addData('project', {'name': 'Test project1', 'objective': 'Test objective1', 'status': 'active', 'comment': '#tag1 #tag2 :field1:1: :field2:max: A random text'})
      viewProj = self.be.db.getView('viewProjects/viewProjects')
      projID  = [i['id'] for i in viewProj][0]
      self.be.changeHierarchy(projID)

      ### add external data
      self.be.addData('measurement', {'name': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/320px-Google_2015_logo.svg.png', 'comment': 'small'}, localCopy=True)
      self.be.addData('measurement', {'name': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/640px-Google_2015_logo.svg.png', 'comment': 'large'})
      projDirName = self.be.basePath+self.be.cwd
      shutil.copy(self.be.softwarePath+'/ExampleMeasurements/Zeiss.tif', projDirName)
      self.be.scanTree()
      print(self.be.output('Measurements'))
      print(self.be.outputMD5())

      ### check consistency of database and replicate to global server
      print('\n*** Check this database ***')
      output = self.be.checkDB()
      print(output)
      self.assertTrue(output.count('**UNSURE')==0,'UNSURE string in output')
      self.assertTrue(output.count('**WARNING')==0,'WARNING string in output')
      self.assertTrue(output.count('**ERROR')==0,'ERROR string in output')
      print('\n*** DONE WITH VERIFY ***')
    except:
      print('ERROR OCCURRED IN VERIFY TESTING\n'+ traceback.format_exc() )
    return


  def tearDown(self):
    try:
      self.be.exit(deleteDB=True)
    except:
      pass
    time.sleep(2)
    if os.path.exists(self.dirName): shutil.rmtree(self.dirName)
    return

if __name__ == '__main__':
  unittest.main()