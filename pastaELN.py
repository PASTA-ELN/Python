#!/usr/bin/python3
""" Main function when command-line commands used

Called by user or react-electron frontend. Keep it simple: only functions that
are required by frontend. Otherwise, make only temporary changes
"""
import os, json, sys
from subprocess import run, PIPE, STDOUT
import argparse, traceback
import urllib.request
from backend import Pasta
from miscTools import upOut, upIn, getExtractorConfig, printQRcodeSticker, checkConfiguration
from inputOutput import importELN, exportELN

#TODO_P2 os -> pathlib: no more change-dir; open branch for it
argparser = argparse.ArgumentParser(usage='''
pastaELN.py <command> [-i docID] [-c content] [-l labels] [-d database]

Possible commands are:
    help: help information
      example: pastaELN.py help
    test: test PASTA setup
      example: pastaELN.py test -d instruments
    updatePASTA: git pull in source
      example: pastaELN.py updatePASTA
    verifyDB: test PASTA database
      example: pastaELN.py verifyDB
      example: pastaELN.py verifyDBdev (repair function)
    verifyConfiguration: test PASTA configuration
      example: pastaELN.py verifyConfiguration
      example: pastaELN.py verifyConfigurationDev (repair function)
    history: get history for docTypes
      example: pastaELN.py history
    saveBackup,loadBackup: save to file.zip / load from file.zip
      - docId is optional as it reduces the scope of the backup
      - database is optional as otherwise the default is used
      example: pastaELN.py saveBackup -d instruments
      example: pastaELN.py saveBackup -i x-76b0995cf655bcd487ccbdd8f9c68e1b
    sync: synchronize / replicate with remote server
    print: print overview
      label: possible docLabels 'Projects', 'Samples', 'Measurements', 'Procedures'
      example: pastaELN.py print -d instruments -l instrument
    printQRCodes: print qr-codes
      content: list of qrCodes and text
      note: requires set -qrPrinter in pasta.json
      example: pastaELN.py printQRCodes -c '[["my random name","Sample 1"], ["","Oven 450C"]]'
    scanHierarchy, hierarchy: scan project with docID
      example: pastaELN.py scanHierarchy -i ....
    saveHierarchy: save hierarchy to database
    addDoc:
      content is required as json-string
      example: pastaELN.py createDoc --content "{'-name':'Instruments','status':'passive','objective':'List of all instruments in IEK2','comment':'result of task force July 2020','docType':'project'}"
    newDB: add/update database configuration. item is e.g.
      '{"test":{"user":"Peter","password":"Parker",...}}'
    extractorScan: get list of all extractors and save into .pastaELN.json
      example: pastaELN.py extractorScan
    decipher: decipher encrypted string
      content: string
    importXLS: import first sheet of excel file into database
      before: ensure database configuration and project exist
      example: pastaELN.py importXLS -d instruments -i x-a803c556bb3b367b1e78901109bd5bf5 -c "~/path/to.xls" -l instrument
      -l is the document type
      afterwards: adopt ontology (views are automatically generated)
    importELN: import .eln file
      example: pastaELN.py importELN -c PASTA.eln
''')
argparser.add_argument('command', help='see above...')
argparser.add_argument('-i','--docID',   help='docID of project; always a long alpha-numeric code', default='')
argparser.add_argument('-c','--content', help='content to save/store', default=None)
argparser.add_argument('-l','--label',   help='label used for printing', default='x0')
argparser.add_argument('-d','--database',help='name of database configuration', default='') #required for be = Pasta(args.database)
args = argparser.parse_args()

## general things that do not require open database
if args.command=='newDB':
  #use new database configuration and store in local-config file
  newDB = json.loads(args.item)
  label = list(newDB.keys()).pop()
  with open(os.path.expanduser('~')+'/.pastaELN.json','r', encoding='utf-8') as f:
    configuration = json.load(f)
  configuration[label] = newDB[label]
  with open(os.path.expanduser('~')+'/.pastaELN.json','w', encoding='utf-8') as f:
    f.write(json.dumps(configuration, indent=2))

elif args.command=='help':
  print("HELP:")
  argparser.print_help()

elif args.command=='up':
  print('up:',upOut(args.docID))

elif args.command=='scramble':
  with open(os.path.expanduser('~')+'/.pastaELN.json','r', encoding='utf-8') as f:
    configuration = json.load(f)
  configBackup  = dict(configuration)
  links = configuration['links']
  changed = False
  for link,site in [(i,j) for i in links.keys() for j in ['local','remote']]:
    if 'user' in links[link][site] and 'password' in links[link][site]:
      links[link][site]['cred'] = upIn(links[link][site]['user']+':'+links[link][site]['password'])
      del links[link][site]['user']
      del links[link][site]['password']
      changed = True
  if changed:
    with open(os.path.expanduser('~')+'/.pastaELN_BAK.json','w', encoding='utf-8') as f:
      f.write(json.dumps(configBackup,indent=2))
    with open(os.path.expanduser('~')+'/.pastaELN.json','w', encoding='utf-8') as f:
      f.write(json.dumps(configuration,indent=2))

elif args.command=='extractorScan':
  with open(os.path.expanduser('~')+'/.pastaELN.json','r', encoding='utf-8') as f:
    configuration = json.load(f)
    pathToExtractors = os.path.dirname(os.path.abspath(__file__))+os.sep+'extractors' \
      if 'extractorDir' not in configuration \
      else configuration['extractorDir']
  extractors = getExtractorConfig(pathToExtractors)
  extractors = [extractors[i]['plots'] for i in extractors if len(extractors[i]['plots'])>0 ] #remove empty entries
  extractors = [i for sublist in extractors for i in sublist]   #flatten list
  extractors = {'/'.join(i):j for (i,j) in extractors}
  print('Found extractors',extractors)
  with open(os.path.expanduser('~')+'/.pastaELN.json','r', encoding='utf-8') as f:
    configuration = json.load(f)
  configuration['extractors'] = extractors
  with open(os.path.expanduser('~')+'/.pastaELN.json','w', encoding='utf-8') as f:
    f.write(json.dumps(configuration, indent=2))
  print('SUCCESS')

elif args.command.startswith('verifyConfiguration'):
  repair = args.command=='verifyConfigurationDev'
  output = checkConfiguration(repair=repair)
  print(output)
  if '**ERROR' in output:
    success = False

elif args.command=='decipher':
  from serverActions import passwordDecrypt
  print(passwordDecrypt(args.content).decode())
  print('SUCCESS')


## Commands that require open PASTA database, but not specific project
else:
  try:
    # open database
    curWorkingDirectory = os.path.abspath(os.path.curdir)
    with open(os.path.expanduser('~')+'/.pastaELN.json','r', encoding='utf-8') as f:
      config = json.load(f)
    if args.database=='':
      args.database = config['default']
    success = True
    initViews, initConfig, resetOntology = False, True, False
    if args.command.startswith('test'):
      #precede with configuration test
      output = checkConfiguration(repair=False)
      print(output)
      if 'ERROR' in output:
        success=False
      #real backend test
      initViews, initConfig = True, True
      if args.command=='testDev':
        resetOntology = True
      # local and remote server test
      urls = ['http://127.0.0.1:5984']
      if config['links'][args.database]['remote']!={}:
        urls.append(config['links'][args.database]['remote']['url'])
      for url in urls:
        try:
          with urllib.request.urlopen(url) as package:
            contents = package.read()
            if json.loads(contents)['couchdb'] == 'Welcome':
              print('CouchDB server',url,'is working: username and password test upcoming')
        except:
          print('**ERROR pma01: CouchDB server not working |',url)
          if url=='http://127.0.0.1:5984':
            raise NameError('**ERROR pma01a: Wrong local server.') from None
    try:
      be = Pasta(linkDefault=args.database, initViews=initViews, initConfig=initConfig,
                 resetOntology=resetOntology)
    except:
      print('**ERROR pma20: backend could not be started.\n'+traceback.format_exc()+'\n\n')
      be = None

    # depending on commands
    if args.command.startswith('test') and be:
      print('database server:',be.db.db.client.server_url)
      print('default link:',be.confLinkName)
      print('database name:',be.db.db.database_name)
      designDocuments = be.db.db.design_documents()
      print('Design documents')
      for item in designDocuments:
        numViews = len(item['doc']['views']) if 'views' in item['doc'] else 0
        print('  ',item['id'], '   Num. of views:', numViews )
      try:
        doc = be.db.getDoc('-ontology-')
        print('Ontology exists on server')
      except:
        print('**ERROR pma02: Ontology does NOT exist on server')
      print('local directory:',be.basePath)
      print('software directory:',be.softwarePath)
      os.chdir(be.softwarePath)
      cmd = ['git','show','-s','--format=%ci']
      output = run(cmd, stdout=PIPE, stderr=STDOUT, check=True)
      print('software version:',' '.join(output.stdout.decode('utf-8').split()[0:2]))

    elif args.command=='updatePASTA':
      #update desktop incl. Python backend
      os.chdir(be.softwarePath)
      os.chdir('..')
      text = run(['git','pull'], stdout=PIPE, stderr=STDOUT, check=True)
      print(text.stdout.decode('utf-8'))
      #ensure requirements are fulfilled
      os.chdir('Python')
      text = run(['git','pull'], stdout=PIPE, stderr=STDOUT, check=True)
      print(text.stdout.decode('utf-8'))
      cmd = ['pip3','install','-r','requirements.txt','--disable-pip-version-check']
      text = run(cmd, stdout=PIPE, stderr=STDOUT, check=True)
      print(text.stdout.decode('utf-8'))

    elif args.command.startswith('verifyDB'):
      repair = args.command=='verifyDBdev'
      output = be.checkDB(verbose=False, repair=repair)
      print(output)
      if '**ERROR' in output:
        success = False

    elif args.command=='history':
      print(be.db.historyDB())

    elif args.command=='syncLR':
      success = be.replicateDB()

    elif args.command=='syncRL':
      print('**ERROR pma03: syncRL not implemented yet')

    elif args.command=='print':
      print(be.output(args.label,True))

    elif args.command=='printQRCodes':
      content = args.content.replace('\\n','\n')
      if content[0]=='"' and content[-1]=='"':
        content = content[1:-1]
      content = json.loads(content)
      printQRcodeSticker(content,
        config['-qrPrinter']['page'],
        config['-qrPrinter']['printer'])

    elif args.command=='saveBackup':   #save to backup file.zip
      if args.docID!='':
        exportELN(be, args.docID)
      else:
        be.backup('backup')

    elif args.command=='loadBackup':   #load from backup file.zip
      be.backup('restore')

    elif args.command=='redo':
      doc = dict(be.getDoc(args.docID))
      doc['-type'] = args.content.split('/')
      be.useExtractors(doc['-branch'][0]['path'], doc['shasum'], doc, extractorRedo=True)  #any path is good since the file is the same everywhere; doc-changed by reference
      if len(doc['-type'])>1 and len(doc['image'])>1:
        be.db.updateDoc({'image':doc['image'], '-type':doc['-type']},args.docID)
        success=True
      else:
        print('**ERROR pma06: error after redo-extraction')
        success=False

    elif args.command=='createDoc':
      from urllib import parse
      content = parse.unquote(args.content)
      doc = json.loads(content)
      docType = doc['docType']
      del doc['docType']
      if len(args.docID)>1 and args.docID!='none':
        be.changeHierarchy(args.docID)
      be.addData(docType,doc)

    elif args.command=='importXLS':
      import pandas as pd
      from commonTools import commonTools as cT  #not globally imported since confuses translation
      if args.docID!='':
        be.changeHierarchy(args.docID)
      data = None
      if os.path.exists(args.content):
        data = pd.read_excel(args.content, sheet_name=0).fillna('')
      else:
        data = pd.read_excel(curWorkingDirectory+os.sep+args.content, sheet_name=0).fillna('')
      for idx, row in data.iterrows():
        doc = dict((k.lower(), v) for k, v in row.items())
        be.addData(args.label, doc )
      success=True

    elif args.command=='importELN':
      path = args.content if args.content[0]==os.sep else curWorkingDirectory+os.sep+args.content
      success = importELN(be, args.database, path)

    else:
      ## Commands that require open database and open project
      if args.docID!='':
        be.changeHierarchy(args.docID)

      if be is None:
        print('Backend does not exist')

      elif args.command=='scanHierarchy':
        be.scanTree()                 #there can not be a callback function

      elif args.command=='saveHierarchy':
        content = args.content.replace('\\n','\n')
        if content[0]=="'" and content[-1]=="'":
          content = content[1:-1]
        elif content[0]=="'" or content[-1]=="'":
          print('**ERROR pma07: something strange occurs with content string')
        ## FOR DEBUGGING OF CONTENT STRING
        # print('---- Ensure beginning & end are correct ----')
        # print(content)
        # print('---- Ensure beginning & end are correct ----')
        success = be.setEditString(content)

      elif args.command=='hierarchy':
        print(be.outputHierarchy(True,True))

      ## Default case for all: unknown
      else:
        print("**ERROR pma08: command in pastaELN.py does not exist |",args.command)
        if be:
          be.exit()
        success = False

    if be:
      be.exit()
    if success:
      print('SUCCESS')
    else:
      print('**ERROR pma09: undefined')
  except:
    print("**ERROR pma10: exception thrown during pastaELN.py"+traceback.format_exc()+"\n")
    raise
