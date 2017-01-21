from django.shortcuts import render, render_to_response, redirect, Http404
from .forms import SubmitForm
from models import Submission, Execution, Method
from uuid import uuid1
from django.http import HttpResponse, JsonResponse
import os
import csv
from worker_stats import *
from main.tasks import start_run, get_latest_result
from exp1 import get_metric_data
from django.conf import settings
from .utils import get_metrics_with_time

def index(request):
    if 'submit_id' not in request.GET:
        form = SubmitForm()
        return render(request, 'main/index.html', {'form': form})
    else:
        return render_to_response('main/board.html')


def submit(request):
    if request.method == 'POST':
        f = SubmitForm(request.POST, request.FILES)
        if f.is_valid():
            u = uuid1()
            s = Submission(uuid=u)
            answer_file = f.cleaned_data['answer_file']
            answer_file.name = 'answer.csv'
            truth_file = f.cleaned_data['truth_file']
            truth_file.name = 'truth.csv'
            s.answer = answer_file
            s.truth = truth_file
            s.type = f.cleaned_data['tasktype']
            redundancy_json, redundancy = get_worker_redundancy(answer_file)
            quality_json, quality = get_worker_quality(answer_file, truth_file)
            s.redundancy = repr(redundancy)
            s.quality = repr(quality)
            s.save()

            # return HttpResponse('success!')
            return redirect('/show/?sid='+str(u))
        else:
            return HttpResponse(str(f.errors))

    else:
        return redirect('/')


def show(request):
    if 'sid' not in request.GET:
        s = Submission.objects.all()
        return render_to_response('main/board.html', {'subs': s})
    else:
        sid = request.GET['sid'].strip()
        try:
            s = Submission.objects.get(uuid=sid)

        except Submission.DoesNotExist:
            return HttpResponse('error!')
        redundancy_json = make_redundancy_table(eval(s.redundancy))
        quality_json = make_quality_table(eval(s.quality))
        mask = 1 << s.type
        methods = Method.objects.extra(where=['type & ' + str(mask) + ' > 0']).values_list('name', flat=True)
        return render_to_response('main/result.html', {
            'redundancy': redundancy_json,
            'quality': quality_json,
            's': s.uuid,
            'methods': methods,
            'metrics': get_metrics_with_time(s.type)
        })


def method(request, sid, method):
    # print sid, method
    # s = Submission.objects.get(uuid=sid)
    try:
        s = Submission.objects.get(uuid=sid)
    except Submission.DoesNotExist:
        raise Http404("Submission not found")
    if request.method == 'GET':
        try:
            result, complete = get_latest_result(s, method)
        except Execution.DoesNotExist:
            raise Http404("Execution Does Not Exist!")
        result.update({'complete': complete})
        return JsonResponse(result, safe=False)
    elif request.method == 'POST':
        sm = sid + '::' + method
        try:
            execution = Execution.objects.get(submission=s, method__name=method)
            return HttpResponse('True')
        except Execution.DoesNotExist:
            task = settings.TASKS.setdefault(sm, {})
            # print '================'
            job = start_run.delay(sid, method)
            task['handler'] = job
            return HttpResponse('True')


def plot(request):
    return render_to_response('main/plot.html')

