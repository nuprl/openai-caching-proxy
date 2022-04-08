# Adapted from https://raw.githubusercontent.com/sampsyo/clusterfutures/master/setup.py
import os
from setuptools import setup

def _read(fn):
    path = os.path.join(os.path.dirname(__file__), fn)
    return open(path, encoding='cp850').read()

setup(
    name='openai-caching-proxy',
    version='1.0.0',
    description='A caching proxy for the OpenAI API',
    author='Arjun Guha',
    author_email='a.guha@northeastern.edu',
    url='https://github.com/nuprl/openai-caching-proxy',
    license='MIT',
    platforms='ALL',
    long_description=_read('README.md'),
    packages=['openai_caching_proxy'],
    install_requires=[
        'openai', 'flask', 'sqlalchemy'
    ],
    python_requires='>=3.8',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
    ],
)
