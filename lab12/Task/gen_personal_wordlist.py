import sys
import itertools
import re

if len(sys.argv) < 2:
    print("Usage: gen_personal_wordlist.py victim.txt", file=sys.stderr)
    sys.exit(1)

fields = {}
with open(sys.argv[1], encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            k,v = line.split(':',1)
            fields[k.strip().lower()] = v.strip()
        else:
            parts = [p.strip() for p in line.split(',') if p.strip()]
            if len(parts) >= 1:
                if 'name' not in fields: fields['name'] = parts[0]
            if len(parts) >= 2 and 'surname' not in fields: fields['surname'] = parts[1]
            if len(parts) >= 3 and 'dob' not in fields: fields['dob'] = parts[2]

def digits_from_dob(dob):
    digits = re.sub(r'\D', '', dob)
    opts = set()
    if len(digits) >= 8:
        opts.add(digits) 
        opts.add(digits[:4]) 
        opts.add(digits[-4:]) 
        opts.add(digits[-2:]) 
        if len(digits) >= 6:
            opts.add(digits[-6:]) 
    else:
        if digits:
            opts.add(digits)
    return list(opts)

def variants(s):
    v = set()
    if not s: return []
    s = s.strip()
    v.add(s)
    v.add(s.lower())
    v.add(s.capitalize())
    
    leet = s.lower().replace('a','@').replace('o','0').replace('i','1').replace('e','3').replace('s','5')
    v.add(leet)
    
    if ' ' in s:
        parts = s.split()
        v.add(''.join([p[0] for p in parts]))
    return list(v)

name = fields.get('name','')
surname = fields.get('surname','')
nickname = fields.get('nickname','')
pet = fields.get('pet','')
dob = fields.get('dob','')

parts = []
for p in (name, surname, nickname, pet):
    if p:
        parts.extend(variants(p))
nums = []
if dob:
    nums.extend(digits_from_dob(dob))
suffixes = ['', '!', '123', '1234', '2020', '2021', '@', '007', '!!', '_', '2022', '1990', '2000']
prefixes = ['', '!', '123', '@']
for p in parts:
    print(p)
combos = set()
for a,b in itertools.permutations(parts, 2):
    combos.add(a + b)
    combos.add(a + '_' + b)
    combos.add(a + '.' + b)
    combos.add(a + b.lower())
for c in list(combos)[:2000]:
    print(c)
for p in parts:
    for n in nums + ['21','22','99','01','07']:
        for suf in suffixes:
            print(f"{p}{n}{suf}")
            print(f"{p.lower()}{n}{suf}")
for pre in prefixes:
    for p in parts:
        print(f"{pre}{p}")
common = ['password', 'qwerty', 'welcome', 'letmein', 'secret']
for p in parts:
    for c in common:
        print(p + c)
        print(p.lower() + c)
if pet:
    for p in parts:
        print(p + pet)
        print(p + pet + '123')
