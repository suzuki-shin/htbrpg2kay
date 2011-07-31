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
def chara(request):
  u"""getならユーザーキャラのデータをjsonで返す
  postならキャラデータの登録する
  """
  chara = request.user.get_chara()
  form = CharaForm()
  if request.method == "POST":
    chara.name = request.form['name']
    chara.put()
    return redirect(url_for('htbrpg2kay/index'))
  return Response(chara.to_json())

@login_required
def chara_edit(request):
  form = CharaForm()
  return render_to_response('htbrpg2kay/chara_edit.html',
                            {'form': form.as_widget()})

def entry_get(request):
  u"""はてなブックマークデータをAPIから取得してdatastoreに保存する
  """
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
  if not e: return

  return Response(e.url)

@login_required
def explore(request):
  u"""ダンジョン（はてなブックマークエントリー）を冒険して 結果をjsonで返す
  """
  url = request.args['url']
  if not url: return Response('invalid url')

  chara = request.user.get_chara()
  entry = Entry.get_entry(url)
  result = chara.explore(entry)

  return Response(result)
