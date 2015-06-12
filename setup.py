from setuptools import setup, find_packages


setup(
    name='frasco-github',
    version='0.2',
    url='http://github.com/frascoweb/frasco-github',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Github integration for Frasco",
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco-users'
    ]
)
