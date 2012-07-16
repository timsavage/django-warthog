from django import forms


FIELDS = {
    'CharField': (
        'Character',
        forms.CharField,
    ),
    'IntegerField': (
        'Integer',
        forms.IntegerField,
    ),
    'EmailField': (
        'Email',
        forms.EmailField,
    )
}


def get_field_choices():
    return [(k, v[0]) for k, v in FIELDS.iteritems()]
