#!/usr/bin/env python
# -*- coding: utf-8 -*-

def create_commit_matrix(revisions):
    import functools

    from gitlog import get_commit_hashes, get_files
    commit_hashes = get_commit_hashes(revisions)

    files = get_files(revisions)

    commit_mtrx = {}
    for f in files:
        commit_mtrx.update([(f, [0 for i in range(len(commit_hashes))])])

    for commit_index in range(len(revisions)):
        commit = revisions[commit_index]
        for f in commit['files']:
            commit_mtrx[f][commit_index]=1

    return commit_mtrx
