import csv
import math
import random

from main.models import Submission


def get_label_set(datafile):
    label_set = []

    f = open(datafile, 'r')
    reader = csv.reader(f)
    next(reader)

    for line in reader:
        _, _, label = line

        if label not in label_set:
            label_set.append(label)

    return label_set


def getaccuracy(datafile, truthfile, e2lpd):
    label_set = get_label_set(datafile)
    # in case that e2lpd does not have data in the truthfile, then we randomly sample a label from label_set
    # assert label_set == ['0', '1'] or label_set == ['1', '0']

    e2truth = {}
    f = open(truthfile, 'r')
    reader = csv.reader(f)
    next(reader)

    for line in reader:
        example, truth = line
        e2truth[example] = truth

    tcount = 0

    for e in e2truth:

        if e not in e2lpd:
            # randomly select a label from label_set
            truth = random.choice(label_set)
            if int(truth) == int(e2truth[e]):
                tcount += 1

            continue

        if type(e2lpd[e]) == type({}):
            temp = 0
            for label in e2lpd[e]:
                if temp < e2lpd[e][label]:
                    temp = e2lpd[e][label]

            candidate = []

            for label in e2lpd[e]:
                if temp == e2lpd[e][label]:
                    candidate.append(label)

            truth = random.choice(candidate)

        else:
            truth = e2lpd[e]

        if int(truth) == int(e2truth[e]):
            tcount += 1

    return tcount * 1.0 / len(e2truth)


def getfscore(datafile, truthfile, e2lpd):
    label_set = get_label_set(datafile)
    # in case that e2lpd does not have data in the truthfile, then we randomly sample a label from label_set
    assert label_set == ['0', '1'] or label_set == ['1', '0']

    e2truth = {}
    f = open(truthfile, 'r')
    reader = csv.reader(f)
    next(reader)

    for line in reader:
        example, truth = line
        e2truth[example] = truth

    fz = 0
    fm_pre = 0
    fm_rec = 0

    for e in e2truth:

        if int(e2truth[e]) == 1:
            fm_rec += 1

        if e not in e2lpd:
            # randomly select a label from label_set
            truth = random.choice(label_set)
            if int(truth) == 1:
                fm_pre += 1
                if int(e2truth[e]) == 1:
                    fz += 1

            continue

        if type(e2lpd[e]) == type({}):
            temp = 0
            for label in e2lpd[e]:
                if temp < e2lpd[e][label]:
                    temp = e2lpd[e][label]

            candidate = []

            for label in e2lpd[e]:
                if temp == e2lpd[e][label]:
                    candidate.append(label)

            truth = random.choice(candidate)

        else:
            truth = e2lpd[e]

        if int(truth) == 1:
            fm_pre += 1
            if int(e2truth[e]) == 1:
                fz += 1

    if fz == 0 or fm_pre == 0:
        return 0.0

    precision = fz * 1.0 / fm_pre
    recall = fz * 1.0 / fm_rec

    return 2.0 * precision * recall / (precision + recall)


def getMAE(datafile, truthfile, e2lpd):
    label_set = get_label_set(datafile)
    # in case that e2lpd does not have data in the truthfile, then we randomly sample a label from label_set

    e2truth = {}
    f = open(truthfile, 'r')
    reader = csv.reader(f)
    next(reader)

    for line in reader:
        example, truth = line
        e2truth[example] = truth

    value = 0

    for e in e2truth:

        if e not in e2lpd:
            # randomly select a label from label_set
            truth = random.choice(label_set)
            value += abs(float(truth) - float(e2truth[e]))
            continue

        if type(e2lpd[e]) == type({}):
            temp = 0
            for label in e2lpd[e]:
                if temp < e2lpd[e][label]:
                    temp = e2lpd[e][label]

            candidate = []

            for label in e2lpd[e]:
                if temp == e2lpd[e][label]:
                    candidate.append(label)

            truth = random.choice(candidate)

        else:
            truth = e2lpd[e]

        value += abs(float(truth) - float(e2truth[e]))

    return value * 1.0 / len(e2truth)


def getRMSE(datafile, truthfile, e2lpd):
    label_set = get_label_set(datafile)
    # in case that e2lpd does not have data in the truthfile, then we randomly sample a label from label_set

    e2truth = {}
    f = open(truthfile, 'r')
    reader = csv.reader(f)
    next(reader)

    for line in reader:
        example, truth = line
        e2truth[example] = truth

    value = 0

    for e in e2truth:

        if e not in e2lpd:
            # randomly select a label from label_set
            truth = random.choice(label_set)
            value += (float(truth) - float(e2truth[e])) ** 2
            continue

        if type(e2lpd[e]) == type({}):
            temp = 0
            for label in e2lpd[e]:
                if temp < e2lpd[e][label]:
                    temp = e2lpd[e][label]

            candidate = []

            for label in e2lpd[e]:
                if temp == e2lpd[e][label]:
                    candidate.append(label)

            truth = random.choice(candidate)

        else:
            truth = e2lpd[e]

        value += (float(truth) - float(e2truth[e])) ** 2

    return math.sqrt(value * 1.0 / len(e2truth))


METRICS = {
    Submission.DM: ['accuracy', 'fscore'],
    Submission.SINGLE: ['accuracy'],
    Submission.NUMERIC: ['MAE', 'RMSE'],
}

EXEC_TYPE = {
    Submission.DM: 'categorical',
    Submission.SINGLE: 'categorical',
    Submission.NUMERIC: 'continuous',
}

METRIC_CALCULATOR = {
    'accuracy': getaccuracy,
    'fscore': getfscore,
    'MAE': getMAE,
    'RMSE': getRMSE,
}


def get_metrics(type):
    return METRICS[type]


def get_metrics_with_time(type):
    metrics = METRICS[type]
    metrics.append('time')
    return metrics


def get_exec_type(type):
    return EXEC_TYPE[type]


def get_metric_calculator(type):
    return METRIC_CALCULATOR[type]

