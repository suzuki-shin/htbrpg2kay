# -*- coding: utf-8 -*-
from django.utils import simplejson as json
from google.appengine.ext import db
from kay.ext.testutils.gae_test_base import GAETestBase
from datetime import datetime
import urllib
from htbrpg2kay.models import (
  MyUser, Chara, Entry, Bookmark,
)


class ModelTest(GAETestBase):
  def tearDown(self):
    for c in [MyUser, Chara, Entry, Bookmark]:
      db.delete(c.all().fetch(100))

  def test_myuser(self):
    user = MyUser(email='test@example.com', first_name=u'testuser')
    user.put()
    # add_chara
    user.add_chara(u'testchara')
    charas = Chara.all().fetch(100)
    self.assertEquals(len(charas), 1)
    self.assertEquals(charas[0].name, 'testchara')
    self.assertEquals(charas[0].user.first_name, 'testuser')
    user2 = MyUser(email='hoge@fuga.com', first_name=u'hoge')
    user2.put()
    user2.add_chara(u'fuga')
    charas2 = Chara.all().filter('user =',user2).fetch(100)
    self.assertEquals(charas2[0].name, 'fuga')
    # get_chara
    chara2 = user2.get_chara()
    self.assertEquals(chara2.name, 'fuga')

  def test_chara(self):
    u = MyUser(email = 'hoge@hoge.com')
    u.put()
    c = u.add_chara('testchara')
    # to_json
    c_json = c.to_json()
    self.assertEquals(c_json,
                      json.dumps({
                        'name': 'testchara',
                        'lv': 1,
                        'exp': 0,
                        'attack': 1,
                        'magic':1,
                        'speed':1,
                        'user': u.email}))

  def test_entry(self):
    e = Entry(title = u'タイトル',
              count = 10,
              url = 'http://hoge.com',
              entry_url = 'http://b.hatena.ne.jp/hoge',
              eid = 1)
    e.put()

    # get_entry
    e2 = Entry(title = u'タイトル2',
              count = 7,
              url = 'http://fuga.com',
              entry_url = 'http://b.hatena.ne.jp/fuga',
              eid = 2)
    e2.put()
    es = Entry.all().fetch(100)
    self.assertEquals(len(es), 2)
    e_ = Entry.get_entry('http://fuga.com')
    self.assertEquals(e_.title, u'タイトル2')
    self.assertEquals(e_.count, 7)
    self.assertEquals(e_.url, 'http://fuga.com')
    self.assertEquals(e_.entry_url, 'http://b.hatena.ne.jp/fuga')
    self.assertEquals(e_.eid, 2)

    # add_entry
    e3 = Entry.add_entry(title = u'htbタイトル',
                         count= 3,
                         url= 'http://example.jp',
                         entry_url='http://entry_url.com',
                         eid= 3)
    es_ = Entry.all().fetch(100)
    self.assertEquals(len(es_), 3)
    self.assertEquals(es_[2].url, 'http://example.jp')

    # get_hatebu_api
    htb = Entry.get_hatebu_api('http://developer.hatena.ne.jp/ja/documents/bookmark/apis/getinfo')
    self.assert_(htb)

    # get_entry
    e4 = Entry.get_entry('http://hoge.com')
    self.assertEquals(e4.title, u'タイトル')
    e5 = Entry.get_entry('http://developer.hatena.ne.jp/ja/documents/bookmark/apis/getinfo')
    self.assertEquals(e5.title, u'はてなブックマークエントリー情報取得API - Hatena Developer Center')

  def test_bookmark(self):
    u = MyUser(email = 'suzuki@hoge.com', first_name = 'shin')
    u.put()
    e = Entry(title = u'タイトル4',
              count = 7,
              url = 'http://fuga.com',
              entry_url = 'http://b.hatena.ne.jp/fuga',
              eid = 4)
    e.put()
    b = Bookmark(user = u'jojo',
                 tags = ["aaa", "bbb"],
                 timestamp = datetime.strptime("2011/07/22 21:22:06",  "%Y/%m/%d %H:%M:%S"),
                 comment = u'コメント',
                 entry = e)
    b.put()
    bs = Bookmark.all().fetch(100)
    self.assertEquals(len(bs), 1)
    # add_bookmarks
    e2 = Entry(title = u'タイトル5',
              count = 100,
              url = 'http://aa.fuga.com',
              entry_url = 'http://b.hatena.ne.jp/fugaxxx',
              eid = 5)
    e2.put()
    bookmarks = [
      {u'comment': u'',
       u'tags': [u'api'],
       u'timestamp': u'2011/07/22 15:36:47',
       u'user': u'cubick'},
      {u'comment': u'\u3053\u308c\u4f7f\u3063\u3066\u306a\u3093\u304b\u3084\u308a\u305f\u3044',
       u'tags': [u'hatena'],
       u'timestamp': u'2011/07/05 23:51:19',
       u'user': u'takuma510'},
    ]
    Bookmark.add_bookmarks(bookmarks, e2)
    bs2 = Bookmark.all().fetch(100)
    self.assertEquals(len(bs2), 3)
    self.assertEquals(bs2[1].user, u'cubick')
    # get_bookmarks
    bs3 = Bookmark.get_bookmarks(e)
    self.assertEquals(len(bs3), 1)
    self.assertEquals(bs[0].user, u'jojo')
