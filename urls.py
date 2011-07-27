# -*- coding: utf-8 -*-
# htbrpg2kay.urls
# 

# Following few lines is an example urlmapping with an older interface.
"""
from werkzeug.routing import EndpointPrefix, Rule

def make_rules():
  return [
    EndpointPrefix('htbrpg2kay/', [
      Rule('/', endpoint='index'),
    ]),
  ]

all_views = {
  'htbrpg2kay/index': 'htbrpg2kay.views.index',
}
"""

from kay.routing import (
  ViewGroup, Rule
)

view_groups = [
  ViewGroup(
    Rule('/', endpoint='index', view='htbrpg2kay.views.index'),
    Rule('/user', endpoint='user', view='htbrpg2kay.views.user'),
  )
]

