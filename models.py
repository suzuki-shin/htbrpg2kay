# -*- coding: utf-8 -*-
# htbrpg2kay.models

import logging
import inspect

from django.utils import simplejson as json
from google.appengine.ext import db
from google.appengine.ext import db
from kay.auth.models import GoogleUser
import kay.db
from datetime import datetime
import urllib

# Create your models here.
class MyUser(GoogleUser):
  def get_adventurer(self):
    u"""ユーザーキャラデータを取得する
    まだキャラが存在しなければ新たに登録する
    """
    adventurers = Adventurer.all().filter('user =', self).fetch(1)
    if adventurers:
      adventurer = adventurers[0]
    else:
      name = self.first_name if self.first_name else self.email
      adventurer = self.add_adventurer(name)
#     adventurer.img = str(adventurer.lv) + '.gif' if adventurer.lv <= 25 else '25.gif'

    return adventurer

  def add_adventurer(self, name):
    adventurer = Adventurer(user = self, name = name)
    adventurer.put()

    return adventurer

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

class Job(SsModel):
  u"""キャラクターの職業
  戦士：
  魔法使い：
  格闘家：
  """
  name   = db.StringProperty(required = True) # 名前
  hp     = db.IntegerProperty(default = 10)   # HP成長ボーナス
  attack = db.IntegerProperty(default = 1)    # 攻撃力成長ボーナス
  guard  = db.IntegerProperty(default = 1)    # 防御力成長ボーナス
  speed  = db.IntegerProperty(default = 1)    # スピード成長ボーナス

class Fighter(Job):
  u"""戦士
  """
  pass
#   def get_attack_power(self, enemy_job):
#     if enemy_job.__class__ == 'Assassin':

class Neet(Job):
  pass

class Chara(SsModel):
  u"""キャラクターデータ
  """
  name   = db.StringProperty(required = True) # 名前
  lv     = db.IntegerProperty(default = 1)    # レベル
  exp    = db.IntegerProperty(default = 0)    # 経験値
  hp     = db.IntegerProperty(default = 10)   # HP
  attack = db.IntegerProperty(default = 1)    # 攻撃力
  guard  = db.IntegerProperty(default = 1)    # 防御力
  speed  = db.IntegerProperty(default = 1)    # スピード
  job    = db.ReferenceProperty(Job)    # 職業

  def to_json(self):
    u"""オブジェクトをJSONにして返す
    """
    attr_list = [(attr, value_or_email(getattr(self, attr))) for attr in self._all_properties]
    attr_dict = dict(attr_list)
    return json.dumps(attr_dict)


class Adventurer(Chara):
  u"""ユーザーキャラクターデータ
  """
  user   = db.ReferenceProperty(MyUser, required = True) # ユーザー

  def explore(self, entry):
    u"""
    """
    bookmarks = entry.get_bookmarks()
    #     results = [res for b in bookmarks: res = self.battle(b) if res['win']]
    battle_result = {'win': True, 'results': []}
    for b in bookmarks:
      res = self.battle(b)
      if not res['win']:
        battle_result['win'] = False
        break

      battle_result['results'].append(res)

    return battle_result

  def battle(self, bookmark):
    u"""戦闘結果を返す
    """
    res = {}
    res['win'] = True                   # 仮
    res['damage'] = 10                  # 仮

    return res


class Enemy(Chara):
  u"""敵キャラ（ブックマーカー）データ
  """
  @classmethod
  def get_enemy(cls, name):
    es = cls.all().filter('name =', name).fetch(1)
    logging.debug(inspect.currentframe().f_lineno)
    logging.debug(es)

    if es: return es[0]

    e = cls.add_enemy(name)
    logging.debug(inspect.currentframe().f_lineno)
    logging.debug(e)

    return e

  @classmethod
  def add_enemy(self, name):
    e = Enemy(name = name)
    e.put()

    return e


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
      entry = cls.add_entry(
        title      = htb.get('title'),
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
    e = Entry.all().filter('eid =', eid).fetch(1)
    if e:
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

  def get_bookmarks(self):
    u"""
    """
    return Bookmark.get_bookmarks(self)


class Bookmark(SsModel):
  u"""はてぶエントリーページについてるブックマーク（モンスターとみなす）
  """
  user      = db.ReferenceProperty(Enemy, required=True)       # ブックマークしたユーザ名
#   user      = db.StringProperty(required=True)       # ブックマークしたユーザ名
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

      enemy = Enemy.get_enemy(bm.get('user'))
      timestamp = datetime.strptime(bm['timestamp'], "%Y/%m/%d %H:%M:%S")
      bookmark = cls(
        user      = enemy,
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


class Skill(SsModel):
  u"""スキル
  """
  name   = db.StringProperty(required = True) # 名前
  timing = db.IntegerProperty(required = True) # 発動タイミング(1:戦闘開始時、2:攻撃時、3:被攻撃時)
  typ   = db.IntegerProperty(required = True) # スキルの種類（1:一時的なパラメタ変化、2:恒久的なパラメタ変化、3:その他）
  param = db.StringProperty()                # 対象パラメタ名
  value = db.IntegerProperty()               # 効果置
  job   = db.ReferenceProperty(Job, True)    # 装備可能職業


class Battle(SsModel):
  u"""戦闘の状態を格納
  """
  adventurer    = db.ReferenceProperty(Adventurer, required = True) # ユーザーキャラ
  enemy         = db.ReferenceProperty(Enemy, required = True) # 敵
  win           = db.BooleanProperty()                           # ユーザー側が勝利したか
  a_damage      = db.IntegerProperty()                         # ユーザーキャラのダメージ
  e_damage      = db.IntegerProperty()                         # モンスターのダメージ
  first         = db.ReferenceProperty(Chara, collection_name = 'first', required = True) # 先攻キャラ
  second        = db.ReferenceProperty(Chara, collection_name = 'second', required = True) # 後攻キャラ
  a_start_skill = db.ReferenceProperty(Skill, collection_name = 'a_start_skill')
  a_attack_skill = db.ReferenceProperty(Skill, collection_name = 'a_attack_skill')
  a_guard_skill = db.ReferenceProperty(Skill, collection_name = 'a_guard_skill')
  e_start_skill = db.ReferenceProperty(Skill, collection_name = 'e_start_skill')
  e_attack_skill = db.ReferenceProperty(Skill, collection_name = 'e_attack_skill')
  e_guard_skill = db.ReferenceProperty(Skill, collection_name = 'e_guard_skill')

  @classmethod
  def do(cls, adventurer, enemy):
    u"""戦闘処理を行う
    """
    # + 両者の戦闘開始時スキル発動判定
    a_start_skill = adventurer.get_skill_start()
    e_start_skill = enemy.get_skill_start()

    # + 先攻判定（どちらが先攻か）

    # + 先攻の攻撃
    #  + 先攻の攻撃時スキル発動判定
    #  + 後攻の被攻撃時スキル発動判定
    #  + ヒット判定
    #  + ダメージ計算
    #  + 両者の生存判定（HPが0以下なら勝敗判定へ）
    # + 後攻の攻撃
    #  + 後攻の攻撃時スキル発動判定
    #  + 先攻の被攻撃時スキル発動判定
    #  + ヒット判定
    #  + ダメージ計算
    #  + 両者の生存判定（HPが0以下なら勝敗判定へ）
    # + 勝敗判定
