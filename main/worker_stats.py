import csv

import gviz_api


def get_worker_redundancy(answer_file):
    reader = csv.reader(answer_file)
    next(reader)
    workers = {}
    for line in reader:
        q, w, a = line
        if w not in workers:
            workers[w] = 1
        else:
            workers[w] += 1
    json = make_redundancy_table(workers)
    return json, workers


def make_redundancy_table(workers):
    description = {('task_id', 'string'): ('num', 'number')}
    data_table = gviz_api.DataTable(description, workers)
    json = data_table.ToJSon(columns_order=('task_id', 'num'))
    return json


def get_worker_quality(answer_file, truth_file):
    reader = csv.reader(answer_file)
    next(reader)
    workers = {}
    for line in reader:
        q, w, a, = line
        q2a = workers.setdefault(w, {})
        q2a[q] = a

    reader = csv.reader(truth_file)
    next(reader)
    q2t = {q: t for (q, t) in reader}

    eps = 1e-6
    for w, q2a in workers.items():
        correct = 0
        for q, a in q2a.items():
            if q in q2t and q2t[q] == a:
                correct += 1
        temp = correct * 1.0 / len(q2a)
        workers[w] = temp if temp < 1.0 else (1 - eps)
    json = make_quality_table(workers)
    return json, workers


def make_quality_table(workers):
    description = {('worker_id', 'string'): ('quality', 'number')}
    data_table = gviz_api.DataTable(description, workers)
    json = data_table.ToJSon(columns_order=('worker_id', 'quality'))
    return json

