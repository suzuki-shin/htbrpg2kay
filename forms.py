# -*- coding: utf-8 -*-

from kay.utils import forms
from kay.utils.forms.modelform import ModelForm

from htbrpg2kay.models import (Chara, Skill)

# class CharaForm(ModelForm):
#   class Meta:
#     model = Chara
#     include = ('name')
class CharaForm(forms.Form):
  name = forms.TextField("Your Chara name", required=True)

class SkillForm(forms.Form):
  name = forms.TextField("Skill name", required=True)
  timing = forms.TextField("Skill timing", required=True)
  typ    = forms.TextField("Skill typ", required=True)
  param  = forms.TextField("Skill param")
  value  = forms.TextField("Skill value")
  job = forms.TextField("Skill job")
