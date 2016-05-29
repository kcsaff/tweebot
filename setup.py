import os
from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession

version = '0.1.1'

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()

install_reqs = parse_requirements('requirements.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(name='tweebot',
      version=version,
      description='A simple twitter-bot command-line tool and library',
      long_description='\n\n'.join((read('README.md'), read('CHANGELOG'))),
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Other Audience',
          'Programming Language :: Python :: 3'],
      author='K.C.Saff',
      author_email='kc@saff.net',
      url='https://github.com/kcsaff/tweebot',
      license='MIT',
      packages=find_packages(),
      install_requires=reqs,
      entry_points={
          'console_scripts': ['tweebot = tweebot:main']
      },
      include_package_data=False,
)
