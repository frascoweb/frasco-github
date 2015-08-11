from setuptools import setup


setup(
    name='frasco-github',
    version='0.3',
    url='http://github.com/frascoweb/frasco-github',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Github integration for Frasco",
    py_modules=['frasco_github'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco-users'
    ]
)
