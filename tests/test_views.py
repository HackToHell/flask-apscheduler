import json

from flask import Flask
from flask_apscheduler import APScheduler
from unittest import TestCase


class TestViews(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SCHEDULER_VIEWS_ENABLED'] = True
        self.scheduler = APScheduler(app=self.app)
        self.scheduler.start()
        self.client = self.app.test_client()

    def test_add_job(self):
        job = {
            'id': 'job1',
            'func': 'test_views:job1',
            'trigger': 'date',
            'run_date': '2020-12-01T12:30:01+00:00',
        }

        response = self.client.post('/scheduler/jobs', data=json.dumps(job))
        self.assertEqual(response.status_code, 200)

        job2 = json.loads(response.get_data(as_text=True))

        self.assertEqual(job.get('id'), job2.get('id'))
        self.assertEqual(job.get('func'), job2.get('func'))
        self.assertEqual(job.get('trigger'), job2.get('trigger'))
        self.assertEqual(job.get('run_date'), job2.get('run_date'))

    def test_delete_job(self):
        self.__add_job()

        response = self.client.delete('/scheduler/jobs/job1')
        self.assertEqual(response.status_code, 204)

        response = self.client.get('/scheduler/jobs/job1')
        self.assertEqual(response.status_code, 404)

    def test_get_job(self):
        job = self.__add_job()

        response = self.client.get('/scheduler/jobs/job1')
        self.assertEqual(response.status_code, 200)

        job2 = json.loads(response.get_data(as_text=True))

        self.assertEqual(job.get('id'), job2.get('id'))
        self.assertEqual(job.get('func'), job2.get('func'))
        self.assertEqual(job.get('trigger'), job2.get('trigger'))
        self.assertEqual(job.get('minutes'), job2.get('minutes'))

    def test_get_all_jobs(self):
        job = self.__add_job()

        response = self.client.get('/scheduler/jobs')
        self.assertEqual(response.status_code, 200)

        jobs = json.loads(response.get_data(as_text=True))

        self.assertEqual(len(jobs), 1)

        job2 = jobs[0]

        self.assertEqual(job.get('id'), job2.get('id'))
        self.assertEqual(job.get('func'), job2.get('func'))
        self.assertEqual(job.get('trigger'), job2.get('trigger'))
        self.assertEqual(job.get('minutes'), job2.get('minutes'))

    def test_update_job(self):
        job = self.__add_job()

        data_to_update = {
            'args': [1]
        }

        response = self.client.patch('/scheduler/jobs/job1', data=json.dumps(data_to_update))
        self.assertEqual(response.status_code, 200)

        job2 = json.loads(response.get_data(as_text=True))

        self.assertEqual(job.get('id'), job2.get('id'))
        self.assertEqual(job.get('func'), job2.get('func'))
        self.assertEqual(data_to_update.get('args'), job2.get('args'))
        self.assertEqual(job.get('trigger'), job2.get('trigger'))
        self.assertEqual(job.get('minutes'), job2.get('minutes'))

    def test_pause_and_resume_job(self):
        self.__add_job()

        response = self.client.post('/scheduler/jobs/job1/pause')
        self.assertEqual(response.status_code, 200)
        job = json.loads(response.get_data(as_text=True))
        self.assertIsNone(job.get('next_run_time'))

        response = self.client.post('/scheduler/jobs/job1/resume')
        self.assertEqual(response.status_code, 200)
        job = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(job.get('next_run_time'))

    def __add_job(self):
        job = {
            'id': 'job1',
            'func': 'test_views:job1',
            'trigger': 'interval',
            'minutes': 10,
        }

        response = self.client.post('/scheduler/jobs', data=json.dumps(job))
        return json.loads(response.get_data(as_text=True))


def job1(x=0):
    print(x)

