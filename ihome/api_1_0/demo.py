# -*- coding: utf-8 -*-
from . import api
import logging
from flask import current_app


@api.route("/index")
def index():
    current_app.logger.error('error mag')
    return 'index page'