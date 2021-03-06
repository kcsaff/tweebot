import os
from setuptools import setup, find_packages

version = '1.0.0'


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


try:
    import pypandoc
    description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    description = read('README.md')


setup(name='tweebot',
      version=version,
      description='A simple twitter-bot command-line tool and library',
      long_description=description,
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Other Audience',
          'Programming Language :: Python :: 3'],
      author='K.C.Saff',
      author_email='kc@saff.net',
      url='https://github.com/kcsaff/tweebot',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'colorama>=0.4.3',
          'requests>=2.24.0',
          'tweepy>=3.8.0'
      ],
      entry_points={
          'console_scripts': ['tweebot = tweebot:main']
      },
      include_package_data=False)
