# -*- coding: utf-8 -*-
"""
htbrpg2kay.views
"""

"""
import logging

from google.appengine.api import users
from google.appengine.api import memcache
from werkzeug import (
  unescape, redirect, Response,
)
from werkzeug.exceptions import (
  NotFound, MethodNotAllowed, BadRequest
)

from kay.utils import (
  render_to_response, reverse,
  get_by_key_name_or_404, get_by_id_or_404,
  to_utc, to_local_timezone, url_for, raise_on_dev
)
from kay.i18n import gettext as _
from kay.auth.decorators import login_required

"""

import logging
import inspect
from django.utils import simplejson as json
from kay.utils import (
  render_to_response, url_for,
)
from werkzeug import (
  unescape, redirect, Response,
)
from kay.auth.decorators import login_required
from  htbrpg2kay.models import (
  Entry,
)
from htbrpg2kay.forms import CharaForm

# Create your views here.

def index(request):
  return render_to_response('htbrpg2kay/index.html', {'message': 'Hello htbrpg2kay'})

@login_required
def adventurer(request):
  u"""getならユーザーキャラのデータをjsonで返す
  postならキャラデータの登録する
  """
  adventurer = request.user.get_adventurer()
  form = CharaForm()
  if request.method == "POST":
    adventurer.name = request.form['name']
    adventurer.put()
    return redirect(url_for('htbrpg2kay/index'))
  return Response(adventurer.to_json())

@login_required
def adventurer_edit(request):
  form = CharaForm()
  return render_to_response('htbrpg2kay/adventurer_edit.html',
                            {'form': form.as_widget()})

def entry_get(request):
  u"""はてなブックマークデータをAPIから取得してdatastoreに保存する
  """
  logging.debug(inspect.currentframe().f_lineno)

  url = request.args['url']
  htb = Entry.get_hatebu_api(url)

  e = Entry.add_entry(
    url        = htb['url'],
    entry_url  = htb['entry_url'],
    eid        = int(htb['eid']),
    title      = htb['title'],
    count      = int(htb['count']),
    screenshot = htb['screenshot'],
    bookmarks  = htb['bookmarks'],
  )
  if not e: return Response('entry add error :' + str(inspect.currentframe().f_lineno))

  return Response(e.url)

@login_required
def explore(request):
  u"""ダンジョン（はてなブックマークエントリー）を冒険して 結果をjsonで返す
  """
  url = request.args['url']
  if not url: return Response('invalid url')

  adventurer = request.user.get_adventurer()
  entry = Entry.get_entry(url)
  result = adventurer.explore(entry)
  logging.debug(inspect.currentframe().f_lineno)
  logging.debug(result)

  return Response(json.dumps(result))
