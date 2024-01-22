from setuptools import setup
from setuptools.command.sdist import sdist 

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='extensible_splines',
    version='0.2.1',
    packages=['extensible_splines'],
    url='https://github.com/egoughnour/extensible-splines',
    license='MIT',
    author='E Goughnour',
    author_email='e.goughnour@gmail.com',
    description='Simple, easily verified custom spline interpolation.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['matplotlib'],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    cmdclass={
        'sdist': sdist
    }
)
