# -*- coding: utf-8 -*-
# htbrpg2kay.models
from django.utils import simplejson as json
from google.appengine.ext import db
from google.appengine.ext import db
from kay.auth.models import GoogleUser
import kay.db

# Create your models here.
class MyUser(GoogleUser):
  def get_chara(self):
    u"""ユーザーらキャラデータを取得する
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

# class Category(db.Model):
#   name = db.StringProperty(required=True)

#   def __unicode__(self):
#     return self.name

# class Comment(db.Model):
#   user = kay.db.OwnerProperty()
#   body = db.TextProperty(required=True, verbose_name=u'Your Comment!!')
#   category = db.ReferenceProperty(Category, collection_name='comments')
#   created = db.DateTimeProperty(auto_now_add=True)

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

#   def to_json(self):
#     u"""オブジェクトをJSONにして返す
#     """
#     attr_list = [(attr, _value_or_key(getattr(self, attr))) for attr in self._all_properties]
#     attr_dict = dict(attr_list)
#     return json.dumps(attr_dict)

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
