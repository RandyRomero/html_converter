from setuptools import setup

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f]

setup(
    name='html_converter',
    version='2019.01.14',
    instal_requires=requirements,
    packages=['html_converter'],
    url='https://github.com/RandyRomero/html_converter/',
    license='MIT License',
    author='Aleksandr Mikheev',
    author_email='ololo.rodriguez@gmail.com',
    description='Microservice based on aiohttp that gets an html file '
                'and returns it as pdf (using athenapdf file converter)'
)


