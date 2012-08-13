from os import path
from setuptools import setup
import warthog

if warthog.VERSION[-1] == 'final':
    CLASSIFIERS = ['Development Status :: 5 - Stable']
elif 'beta' in warthog.VERSION[-1]:
    CLASSIFIERS = ['Development Status :: 4 - Beta']
else:
    CLASSIFIERS = ['Development Status :: 3 - Alpha']

CLASSIFIERS += [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]

setup(
    author="Tim Savage",
    author_email="tim.savage@poweredbypenguins.org",
    name='django-warthog',
    version=warthog.__version__,
    description='Embeddable CMS for Django.',
    long_description=open(path.join(path.dirname(__file__), 'README')).read(),
    #url='',
    license='BSD License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django>=1.4',
        ],
    packages=[
        'warthog',
        'warthog.admin',
        'warthog.migrations',
        'warthog.templatetags',
        'warthog.templatevars',
        'warthog.tests',
        ],
    package_data={
        'warthog': [
            'static/admin/css/warthog.css',
            'static/admin/css/img/warthog-sprite.png',
            'templates/admin/warthog/resource/*.html',
            'templates/admin/warthog/*.html',
            'templates/warthog/*.html',
        ],
    },
)
