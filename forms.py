# -*- coding: utf-8 -*-

from kay.utils import forms
from kay.utils.forms.modelform import ModelForm

from htbrpg2kay.models import Chara

# class CharaForm(ModelForm):
#   class Meta:
#     model = Chara
#     include = ('name')
class CharaForm(forms.Form):
  name = forms.TextField("Your Chara name", required=True)
