"""
referrals-bokeh
A collection of Bokeh apps in a dashboard that displays referral conversion process
measures for specialty clinics.  This is an example of work by Steven J Leathard posted
to my GitHub site.
https://907sjl.github.io/
"""

import os

from jinja2 import Environment, FileSystemLoader
from tornado.web import RequestHandler, StaticFileHandler

from bokeh.server.server import Server
from bokeh.server.views.static_handler import StaticHandler
from bokeh.application import Application 
from bokeh.application.handlers.function import FunctionHandler

from datetime import date

import app.ClinicProcessApp as cpa
import app.CRMUsageApp as cua
import app.PendingReferralsApp as pra
import app.RoutinePerformanceApp as rpa
import app.UrgentPerformanceApp as upa
import app.SeenTimesApp as sta
import app.ScheduleTimesApp as scta


# global tornado environment for this module
env = Environment(loader=FileSystemLoader('templates'))


# Tornado request handlers for static-ish pages

class IndexHandler(RequestHandler):
    # Tornado event handler to process HTTP requests to a pre-configured path
    # all this does is inject text variables into a Jinja2 template file to create HTML 
    def get(self):
        # load the Jinja2 template
        template = env.get_template('index.html')
        # return the HTTP response with HTML generated from the template
        self.write(template.render(app_root=r'referrals',
                                   today_long=date.today().strftime("%A, %B %d, %Y"),
                                   report_month='October 2022',
                                   template="Tornado"))
# END CLASS IndexHandler


class CoverHandler(RequestHandler):
    # Tornado event handler to process HTTP requests to a pre-configured path 
    # all this does is inject text variables into a Jinja2 template file to create HTML 
    def get(self):
        # load the Jinja2 template
        template = env.get_template('cover.html')
        # return the HTTP response with HTML generated from the template
        self.write(template.render(app_root=r'referrals',
                                   today_long=date.today().strftime("%A, %B %d, %Y"),
                                   report_month='October 2022',
                                   template="Tornado"))
# END CLASS CoverHandler


# MAIN script - run on execution

# The `static/` end point is reserved for Bokeh resources, as specified in
# bokeh.server.urls. In order to make your own end point for static resources,
# add the following to the `extra_patterns` argument, replacing `DIR` with the desired directory.
# (r'/DIR/(.*)', StaticFileHandler, {'path': os.path.normpath(os.path.dirname(__file__) + '/DIR')})
apps = {'/referrals/scheduled': Application(FunctionHandler(scta.schedule_times_app_handler)),
        '/referrals/seen': Application(FunctionHandler(sta.seen_times_app_handler)),
        '/referrals/routine': Application(FunctionHandler(rpa.routine_performance_app_handler)),
        '/referrals/urgent': Application(FunctionHandler(upa.urgent_performance_app_handler)),
        '/referrals/referrals': Application(FunctionHandler(cpa.clinic_process_app_handler)),
        '/referrals/crm': Application(FunctionHandler(cua.crm_usage_app_handler)),
        '/referrals/pending': Application(FunctionHandler(pra.pending_referrals_app_handler))}
routes = [('/referrals/cover', CoverHandler),
          ('/', IndexHandler),
          ('/referrals', IndexHandler),
          (r'/referrals/css/(.*)', StaticFileHandler, {'path': os.path.normpath(os.path.dirname(__file__) + '/css')}),
          (r'/referrals/images/(.*)',
          StaticFileHandler,
          {'path': os.path.normpath(os.path.dirname(__file__) + '/images')}),
          (r'/referrals/static/(.*)', StaticHandler, {})]

server = Server(apps, port=5005, extra_patterns=routes)
server.start()

if __name__ == '__main__':
    print('Open Tornado app with embedded Bokeh application on http://localhost:5005/')
    print('Current working directory is: ', os.getcwd())
    if not os.getcwd().endswith('referrals-bokeh'):
        os.chdir(r'.\referrals-bokeh')
        print('...changing working directory to app folder: ', os.getcwd())

    # The following line will open a browser page on a client and load the app
#    server.io_loop.add_callback(view, "http://localhost:5005/")

    # The following line will silently initiate and endless polling loop for messages
    server.io_loop.start()
