import math, csv, os, random
import time, commands, redis
python_command = 'python '
methods_folder = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + 'methods'

def get_latest_result(s, method):
    r = redis.Redis()
    p = r.pipeline()
    key = s.uuid + '::' + method
    items = ['current_accuracy', 'current_fscore', 'total_accuracy', 'total_fscore']
    for i in items:
        p.hget(key, i)
    result = p.execute()
    return result


def start_run(s, method):
    iterations = 1
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
    accuracies = []
    fscores = []
    times = []
    r = redis.Redis()
    key = s.uuid + '::' + method
    for iteration in range(iterations):
        tempaccuracies = []
        tempfscores = []
        temptime = []
        for foldno in range(s.kfold):
            datafile = "'" + kfolder + os.path.sep + str(iteration) + os.path.sep + "answer_" + str(foldno) + ".csv'"

            starttime = time.time()
            output = commands.getoutput(python_command + methods_folder+ os.path.sep + method + r'/method.py '
                                        + datafile + ' ' + '"categorical"' ).split('\n')[-1]
            duration = time.time() - starttime

            accuracy = getaccuracy(eval(datafile), eval(truthfile), eval(output))
            fscore = getfscore(eval(datafile), eval(truthfile), eval(output))

            temptime.append(str(duration))
            tempaccuracies.append(str(accuracy))
            tempfscores.append(str(fscore))

            r.hset(key, 'current_time', temptime)
            r.hset(key, 'current_accuracy', tempaccuracies)
            r.hset(key, 'current_fscore', tempfscores)

            print method + str(iteration) + '_' + str(foldno) + ':' + str(duration)

        times.append(temptime)
        accuracies.append(tempaccuracies)
        fscores.append(tempfscores)
        r.hset(key, 'total_time', times)
        r.hset(key, 'total_accuracy', accuracies)
        r.hset(key, 'total_fscore', fscores)

    folder = dataset_dir + os.path.sep + "output"
    if not os.path.isdir(folder):
        os.mkdir(folder)

    folder = folder + os.path.sep + "exp1"
    if not os.path.isdir(folder):
        os.mkdir(folder)

    # time
    f = open(folder + os.path.sep + 'time_' + method, 'w')
    for tempresults in times:
        f.write('\t'.join(tempresults) + '\n')
    f.close()

    # accuracy
    f = open(folder + os.path.sep + 'accuracy_' + method, 'w')
    for tempresults in accuracies:
        f.write('\t'.join(tempresults) + '\n')
    f.close()

    # fscore
    f = open(folder + os.path.sep + 'fscore_' + method, 'w')
    for tempresults in fscores:
        f.write('\t'.join(tempresults) + '\n')
    f.close()


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


def get_label_set(datafile):
    label_set=[]

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
    assert label_set == ['0', '1'] or label_set == ['1', '0']

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
            #randomly select a label from label_set
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

    return tcount*1.0/len(e2truth)


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
            #randomly select a label from label_set
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

    precision = fz*1.0/fm_pre
    recall = fz*1.0/fm_rec

    return 2.0*precision*recall/(precision + recall)