from __future__ import absolute_import
from celery import shared_task
from .models import Submission, Execution
import math, csv, os, random
import time, commands, redis
from .exp1 import get_metric_data
from django.conf import settings
python_command = 'python '
methods_folder = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + 'methods'
from .utils import get_metrics, get_exec_type, get_metric_calculator


def get_latest_result(s, method, metric='accuracy'):
    execution = Execution.objects.get(submission=s, method=method)
    if execution.status == Execution.DONE:
        r = eval(execution.result)
        return r, True
    elif execution.status == Execution.RUNNING:
        r = redis.Redis()
        p = r.pipeline()
        key = s.uuid + '::' + method
        metrics = get_metrics(s.type)
        items = []
        for m in metrics:
            items.extend(['total_' + m, 'current_' + m])
        items.extend(['total_time', 'current_time'])
        for i in items:
            p.hget(key, i)
        temp = p.execute()
        # print temp
        r = []
        for i in temp:
            try:
                r.append(eval(i))
            except TypeError:
                r.append(None)
        # try:
        #     r = [eval(i) for i in temp]
        # except TypeError:
        #     r = [None for i in items]

        aggregated_results = {}
        for idx, m in enumerate(metrics):
            aggregated_results[m] = get_metric_data(r[idx * 2], r[idx * 2 + 1])
        aggregated_results['time'] = get_metric_data(r[-2], r[-1])

        complete = False
        return aggregated_results, complete
    else:
        raise Execution.DoesNotExist


@shared_task
def start_run(sid, method):
    s = Submission.objects.get(uuid=sid)

    execution = Execution.objects.create(submission=s, method_id=method, status=Execution.RUNNING)

    iterations = 10
    dataset_dir = os.path.dirname(os.path.realpath(s.answer.name))
    kfolder = dataset_dir + os.path.sep + 'kfolder'
    if not s.generated_k_folder:
        kfold = generate_kfolderdata(kfolder, iterations, s.answer)
        s.kfold = kfold
        s.generated_k_folder = True
        s.save()

    # if not os.path.isdir(r'./methods/' + method):
    #     pass

    # dataset & method

    truthfile = "'" + s.truth.name + "'"
    metrics = get_metrics(s.type)
    total_metrics = {i: [] for i in metrics}
    times = []
    r = redis.Redis()
    key = s.uuid + '::' + method
    exec_type = get_exec_type(s.type)

    for iteration in range(iterations):
        temp_metrics = {i: [] for i in metrics}
        temptime = []
        for foldno in range(s.kfold):
            datafile = "'" + kfolder + os.path.sep + str(iteration) + os.path.sep + "answer_" + str(foldno) + ".csv'"

            starttime = time.time()
            exec_command = python_command + "'" + methods_folder + os.path.sep + method + \
                           r"/method.py' " + datafile + ' ' + "'" + exec_type + "'"

            output = commands.getoutput(exec_command).split('\n')[-1]
            duration = time.time() - starttime

            temp_result = {}
            for m in metrics:
                temp_result[m] = get_metric_calculator(m)(eval(datafile), eval(truthfile), eval(output))
                temp_metrics[m].append(str(temp_result[m]))
                r.hset(key, 'current_' + m, repr(temp_metrics[m]))

            temptime.append(str(duration))
            r.hset(key, 'current_time', repr(temptime))

            print method + str(iteration) + '_' + str(foldno) + ':' + str(duration)

        times.append(temptime)
        for m in metrics:
            total_metrics[m].append(temp_metrics[m])
            r.hset(key, 'total_' + m, repr(total_metrics[m]))
        r.hset(key, 'total_time', repr(times))

    folder = dataset_dir + os.path.sep + "output"
    if not os.path.isdir(folder):
        os.mkdir(folder)

    folder = folder + os.path.sep + "exp1"
    if not os.path.isdir(folder):
        os.mkdir(folder)

    for m in metrics:
        f = open(folder + os.path.sep + m + '_' + method, 'w')
        for tempresults in total_metrics[m]:
            f.write('\t'.join(tempresults) + '\n')
        f.close()

    # time
    f = open(folder + os.path.sep + 'time_' + method, 'w')
    for tempresults in times:
        f.write('\t'.join(tempresults) + '\n')
    f.close()

    aggregated_results = {}
    for m in metrics:
        aggregated_results[m] = get_metric_data(total_metrics[m])

    aggregated_results['time'] = get_metric_data(times)
    execution.result = repr(aggregated_results)
    execution.status = Execution.DONE
    execution.save()

    return True


def select_kfold(datafile):
    reader = csv.reader(datafile)
    next(reader)

    count = 0
    examples = {}
    for line in reader:
        example, worker, label = line
        examples[example] = 0
        count += 1

    return int(math.ceil(count*1.0/len(examples)))


def generate_kfolderdata(kfolddir, iterations, answer_f):
    if os.path.isdir(kfolddir):
        import shutil
        shutil.rmtree(kfolddir)

    os.mkdir(kfolddir)

    kfold = select_kfold(answer_f)
    print kfold

    for iteration in range(iterations):
        shuffle_data(answer_f, kfold, kfolddir, iteration)

    return kfold


def gete2wl(record):
    e2wl = {}
    for line in record:
        example, worker, label = line
        if example not in e2wl:
            e2wl[example] = []
        e2wl[example].append([worker,label])

    return e2wl

def generaterows(e2wl, redundancy):
    rows = []
    for example in e2wl:
        wl = e2wl[example][:redundancy]
        for worker, label in wl:
            rows.append([example, worker, label])

    return rows

def shuffle_data(answer_f, kfold, kfolddir, iteration):

    folder = kfolddir + os.path.sep + str(iteration)
    if not os.path.isdir(folder):
        os.mkdir(folder)

    record = read_datafile(answer_f)

    random.seed(iteration)
    random.shuffle(record)

    e2wl = gete2wl(record)

    for i in range(kfold):
        csvfile_w = file(folder+'/answer_'+str(i)+'.csv', 'wb+')
        writer = csv.writer(csvfile_w)
        temp=[['question', 'worker', 'answer']]
        writer.writerows(temp)
        if i != kfold-1:
            writer.writerows(generaterows(e2wl, i+1))
        else:
            writer.writerows(record[0:])
        csvfile_w.close()


def read_datafile(datafile):

    record = []
    reader = csv.reader(datafile)
    next(reader)

    for line in reader:
        record.append(line)

    return record


