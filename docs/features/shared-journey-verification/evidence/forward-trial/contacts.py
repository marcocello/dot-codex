import argparse, csv, sqlite3, sys
p=argparse.ArgumentParser()
p.add_argument('--db',required=True)
p.add_argument('--owner',required=True)
s=p.add_subparsers(dest='action',required=True)
a=s.add_parser('add');a.add_argument('name');a.add_argument('email')
s.add_parser('list');s.add_parser('export')
x=p.parse_args()
c=sqlite3.connect(x.db)
c.execute('CREATE TABLE IF NOT EXISTS contacts (owner TEXT,name TEXT,email TEXT,UNIQUE(owner,email))')
if x.action=='add':
 try:
  c.execute('INSERT INTO contacts VALUES (?,?,?)',(x.owner,x.name,x.email));c.commit()
 except sqlite3.IntegrityError:
  print('duplicate email',file=sys.stderr);sys.exit(2)
else:
 rows=c.execute('SELECT name,email FROM contacts WHERE owner=? ORDER BY email',(x.owner,)).fetchall()
 if x.action=='list':
  import json;print(json.dumps(rows))
 else:
  w=csv.writer(sys.stdout);w.writerow(['name','email']);w.writerows(rows)
