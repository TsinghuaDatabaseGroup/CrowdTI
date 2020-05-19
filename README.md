# CrowdTI
CrowdTI is a truth inference system in crowdsourcing which makes three contributions. Firstly, since there are dozens of truth inference algorithms, our system has implemented all of these algorithms and can automatically recommend the best inference algorithm to infer the truth of each task. Secondly, our system can help users to infer the worker quality. Thirdly, our system can visualize the results, including the inference quality and time, worker quality, and task statistics.

### Dependency (Deployment on OS X)
#### celery
Follow instructions at [here](http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#first-steps)

Briefly you can use brew to install rabbitmq needed by celery.
```
brew install rabbitmq
```
After installing, you should alter environment variable PATH as below:
```
export PATH=$PATH:/usr/local/sbin
```
Then install celery using pip

```
pip install celery
```
If you have problems with celery and django, you can refer to [this](http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html)
#### gviz_api
```
pip install -U https://github.com/google/google-visualization-python/zipball/master
```
### mono
Please refer [here](http://www.mono-project.com/) to install mono, in order to compile and run .NET application.
### MATLAB
Please install MATLAB and make sure you can open it in terminal using 'matlab'.

#### jquery.timers
Have already contained in project.
More info [here](https://github.com/patryk/jquery.timers).

#### Database configuration
The project used django default database, you can use your own as long as you configure it in CrowdInfer/settings.py, you can refer to [here](https://docs.djangoproject.com/en/1.10/ref/settings/#databases) for instructions.
### Tested Environment
####OS X 10.11
- Python 2.7.10
- Django 1.10.1
- rabbitmq 3.6.1
- celery 4.0.2
- mono 4.2.3
- MATLAB R2014b

### Make it Run
#### Start rabbitmq
#### Start celery
```
celery -A CrowdInfer worker -l info
```
#### Migrate Django Tables
```
python manage.py migrate
```
Then you should load method info from 'main_method.sql'
#### Run Django
```
python manage.py runserver
```

### Troubleshooting
If you're encountered with error like
> DisabledBackend' object has no attribute '_get_task_meta_for

Make sure you have prepared CrowdInfer/__init__.py as instructions.
