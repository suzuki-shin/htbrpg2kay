# -*- coding: utf-8 -*-
# htbrpg2kay.models

from django.utils import simplejson as json
from google.appengine.ext import db
from google.appengine.ext import db
from kay.auth.models import GoogleUser
import kay.db
from datetime import datetime
import urllib
import logging

# Create your models here.
class MyUser(GoogleUser):
  def get_chara(self):
    u"""ユーザーキャラデータを取得する
    """
    charas = Chara.all().filter('user =', self).fetch(1)
    if charas:
      chara = charas[0]
    else:
      name = self.first_name if self.first_name else self.email
      chara = self.add_chara(name)
#     chara.img = str(chara.lv) + '.gif' if chara.lv <= 25 else '25.gif'

    return chara

  def add_chara(self, name):
    chara = Chara(user = self, name = name)
    chara.put()

    return chara

def value_or_email(value):
  u"""emailプロパティをもっていたらemailを返す。なければそのままの値を返す
  """
  try:
    if value.email:
      return value.email
    else:
      return value
  except AttributeError:
    return value

class SsModel(db.Model):
  u"""モデルクラスの共通の親
  """

class Chara(SsModel):
  u"""ユーザーキャラクターデータ
  """
  name   = db.StringProperty(required = True) # 名前
  lv     = db.IntegerProperty(default = 1)    # レベル
  exp    = db.IntegerProperty(default = 0)    # 経験値
  attack = db.IntegerProperty(default = 1)    # 攻撃力
  magic  = db.IntegerProperty(default = 1)    # 魔力
  speed  = db.IntegerProperty(default = 1)    # スピード
  user   = db.ReferenceProperty(MyUser, required = True)     # ユーザー

  def to_json(self):
    u"""オブジェクトをJSONにして返す
    """
    attr_list = [(attr, value_or_email(getattr(self, attr))) for attr in self._all_properties]
    attr_dict = dict(attr_list)
    return json.dumps(attr_dict)

class Entry(SsModel):
  u"""はてぶエントリーページ（ダンジョンと見なす）
  """
  title      = db.TextProperty()    # タイトル
  count      = db.IntegerProperty() # ブックマークしている合計ユーザ数
  url        = db.StringProperty(required=True) # ブックマークされているURL
  entry_url  = db.StringProperty(required=True) # はてなブックマークエントリーページのURL
  screenshot = db.StringProperty()      # スクリーンショット画像のURL
  eid        = db.IntegerProperty(required=True)     # エントリーID

  @classmethod
  def get_entry(cls, url):
    u"""urlからエントリデータを取得する
    """
    entries = cls.all().filter('url =', url).fetch(1)
    if entries:
      entry = entries[0]
    else:
      htb = cls.get_hatebu_api(url)
      entry = cls.add_entry(title      = htb.get('title'),
                            entry_url  = htb.get('entry_url'),
                            eid        = int(htb.get('eid')),
                            url        = htb.get('url'),
                            count      = int(htb.get('count')),
                            screenshot = htb.get('screenshot'),
                            bookmarks  = htb.get('bookmarks'))

    return entry

  @classmethod
  def get_hatebu_api(cls, url):
    u"""
    """
    api_url = "http://b.hatena.ne.jp/entry/jsonlite/"
    htb_json = urllib.urlopen(api_url + url).read()
    htb = json.loads(htb_json)

    return htb

  @classmethod
  def add_entry(cls,
                url, entry_url, eid,
                title = '', count = 0, 
                screenshot = '', bookmarks = {}):
    u"""エントリデータを登録する
    """

    # TODO 同じeidがあったら登録しないでNoneを返す
    if Entry.all().filter('eid =', eid).fetch(1):
      return None

    entry = cls(
      title      = title,
      count      = count,
      url        = url,
      entry_url  = entry_url,
      screenshot = screenshot,
      eid        = eid,
    )
    entry.put()
    Bookmark.add_bookmarks(bookmarks, entry);

    return entry

  @classmethod
  def add_or_update_entry(cls,
                          url, entry_url, eid,
                          title = '', count = 0,
                          screenshot = '', bookmarks = {}):
    e = cls.add_entry(url, entry_url, eid, title,
                      count, screenshot, bookmarks)
    if e: return e

    e = Entry(url        = url,
              entry_url  = entry_url,
              eid        = eid,
              title      = title,
              count      = count,
              screenshot = screenshot,
              bookmarks  = bookmarks)
    e.put()

    return e

#   def explore(self, user):
#     u"""
#     """
#     bookmarks = self.get_bookmarks()

#     return bookmarks

#   def get_bookmarks(self):
#     u"""
#     """
#     return Bookmark.get_bookmarks(self)


class Bookmark(SsModel):
  u"""はてぶエントリーページについてるブックマーク（モンスターとみなす）
  """
  user      = db.StringProperty(required=True)       # ブックマークしたユーザ名
  tags      = db.StringListProperty()   # タグの配列
  timestamp = db.DateTimeProperty() # ブックマークした時刻。new Date(timestamp) で JavaScript の Date オブジェクトになります
  comment   = db.StringProperty()   # ブックマークコメント
  entry     = db.ReferenceProperty(Entry, required=True) # 所属エントリ

  @classmethod
  def add_bookmarks(cls, bookmarks, entry):
    u"""ブックマークデータを登録する
    """
    for bm in bookmarks:
      if not bm.has_key('user'): continue

      timestamp = datetime.strptime(bm['timestamp'], "%Y/%m/%d %H:%M:%S")
      bookmark = cls(
        user      = bm.get('user'),
        tags      = bm.get('tags'),
        timestamp = timestamp,
        comment   = bm.get('comment'),
        entry     = entry,
      )
      bookmark.put()

    return

  @classmethod
  def get_bookmarks(cls, entry):
    u"""指定したエントリにひもづくブックマークデータを取得する
    """
    bookmarks = cls.all().filter('entry =', entry).fetch(100)

    return bookmarks
