# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    porch.forms
    ~~~~~~~~~~~

    Web Forms
'''

# Import python libs
import logging

# Import 3rd-party libs
import pytz
from wtforms import *
from wtforms.fields import *
from wtforms.validators import *
from wtforms.fields import SubmitField as BaseSubmitField
from babel.dates import get_timezone_name
from werkzeug.datastructures import MultiDict
from jinja2 import Markup
from flask_wtf import Form

# Import porch libs
from porch.application import *

__SKIP_ZONES = (
    'America/Argentina/Salta',
    'Asia/Kathmandu',
    'America/Matamoros',
    'Asia/Novokuznetsk',
    'America/Ojinaga',
    'America/Santa_Isabel',
    'America/Santarem'
)

log = logging.getLogger(__name__)


@cache.memoize(3600)
def build_timezones(locale=None):
    log.debug('Building Timezones for locale: {0}'.format(locale))
    timezones = {}
    for tz in pytz.common_timezones:
        if tz.startswith('Etc/') or tz.startswith('GMT') or tz in __SKIP_ZONES:
            continue
        timezones[u'{0} - {1}'.format(tz,
                                      get_timezone_name(pytz.timezone(tz), locale=locale))] = tz
    return [(timezones[key], key) for key in sorted(timezones.keys())]


class SubmitField(BaseSubmitField):

    _secondary_class_ = ''

    def __call__(self, *args, **kwargs):
        class_ = set(kwargs.pop('class_', '').split())
        class_.add('btn')
        class_.add(self._secondary_class_)
        kwargs['class_'] = ' '.join(class_)
        return super(SubmitField, self).__call__(*args, **kwargs)


class PrimarySubmitField(SubmitField):

    _secondary_class_ = 'btn-primary'


class CancelSubmitField(SubmitField):

    _secondary_class_ = 'btn-warning'


class SensibleSubmitField(SubmitField):

    _secondary_class_ = 'btn-danger'


class FormBase(Form):
    def __init__(self, formdata=None, *args, **kwargs):
        if formdata and not isinstance(formdata, MultiDict):
            formdata = MultiDict(formdata)
        super(FormBase, self).__init__(formdata, *args, **kwargs)

    def validate(self, extra_validators=None):
        rv = super(Form, self).validate()
        errors = []
        if 'csrf' in self.errors:
            del self.errors['csrf']
            errors.append(
                _('Form Token Is Invalid. You MUST have cookies enabled.')
            )
        for field_name, ferrors in self.errors.iteritems():
            errors.append(
                '<b>{0}:</b> {1}'.format(
                    self._fields[field_name].label.text, '; '.join(ferrors)
                )
            )
        if errors:
            flash(
                Markup(
                    '<h4>{0}</h4>\n<ul>{1}</ul>'.format(
                        _('Errors:'),
                        ''.join(['<li>{0}</li>'.format(e) for e in errors])
                    )
                ), "error"
            )
        return rv


class DBBoundForm(FormBase):
    def __init__(self, db_entry=None, formdata=None, *args, **kwargs):
        self.db_entry = db_entry
        super(DBBoundForm, self).__init__(formdata, *args, **kwargs)

    def process(self, formdata=None, *args, **kwargs):
        fields = {}
        for name in self._fields.keys():
            value = getattr(self.db_entry, name, None)
            if value:
                self._fields[name].value_from_db = fields[name] = value
        fields.update(kwargs)
        super(DBBoundForm, self).process(formdata, *args, **fields)
