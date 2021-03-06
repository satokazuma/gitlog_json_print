#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, json, re, csv, sys, functools
from jubatus.recommender import client
from jubatus.recommender import types
from jubatus.common import Datum

def partial_commit_json():
    dump =subprocess.check_output( ['git', 'log', '--pretty=format:{%n  \"commit\": \"%H\",%n  \"author\": \"%an <%ae>\",%n  \"date\": \"%ad\",%n  \"message\": \"%f\"%n},'] ).decode('UTF-8')
    return json.loads("[" + dump[:-1] + "]")

def update_files_per_revision():
    dump =subprocess.check_output( ['git', '--no-pager', 'log', '--name-only', '--format=\'%H', '--pretty=format:'] ).decode('UTF-8')
    chunk=[]
    for x in re.split('\n\n', dump):
        chunk.append([xx for xx in re.split('\n', x) if len(xx)!=0])
    return chunk

def merge(j, f):
    return dict([('author', j['author']), ('message', j['message']), ('commit', j['commit']),('date', j['date']),('files', f)])

def get_log_as_json():
    return list(map(merge, partial_commit_json(), update_files_per_revision()))

log_as_json = get_log_as_json()

commits=[revision['commit'] for revision in log_as_json]

files=list(functools.reduce(lambda acc,e: acc.union(e['files']), log_as_json,set()))

log_csv={}
# initialize the matrix(file, commit). its elements are zero.
for f in files:
    log_csv.update([(f, [0 for x in range(len(commits))])])

for commit_index in range(len(log_as_json)):
    commit = log_as_json[commit_index]
    for f in commit['files']:
        log_csv[f][commit_index]=1

recommender = client.Recommender("127.0.0.1", 9199, "my_recommender")

for filename,cmts in log_csv.items():
    d={}
    for i in range(len(cmts)):
        d.update([(commits[i], cmts[i])])
    recommender.update_row(filename, Datum(d))

relation_map={}
for f in files:
    r = [x.id for x in recommender.similar_row_from_id(f, 4)]
    # print(r[0] + ' -> ' + ', '.join(r[1:]))
    relation_map.update([(f, [x for x in r[1:]])])

print(relation_map)

# print(relation_map)
# [file1, file2, ll]
sorted_names=sorted(relation_map.keys())

def create_link(name):
    def get_index_by_name(name):
        return sorted_names.index(name)

    idx=get_index_by_name(name)
    related_indice=[get_index_by_name(n) for n in relation_map[name] if (n in sorted_names)]
    return [{'source': idx, 'target': i, 'value': 1} for i in related_indice if i > idx]

a = [create_link(n) for n in sorted_names]

with open('hoge.json', 'w') as f:
    json.dump({'nodes': [{'name': name, 'group': 1} for name in sorted_names],
    'links': [e for aa in a for e in aa]}, f,indent=2)
