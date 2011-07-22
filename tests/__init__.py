# -*- coding: utf-8 -*-
from django.utils import simplejson as json
from google.appengine.ext import db
from kay.ext.testutils.gae_test_base import GAETestBase
from htbrpg2kay.models import (
  MyUser, Chara,
)

class ModelTest(GAETestBase):
  def tearDown(self):
    db.delete(MyUser.all().fetch(10))
    db.delete(Chara.all().fetch(10))

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
