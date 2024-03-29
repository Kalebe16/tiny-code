from setuptools import find_packages, setup

from tiny_code.version import __version__

setup(
    name='tiny-code',
    version=__version__,
    author='Kalebe Chimanski de Almeida',
    description='This tool is a estupid simple tiny code editor',
    entry_points={
        'console_scripts': [
            'tiny-code=tiny_code.__main__:run_app',
        ],
    },
    packages=find_packages(),
    package_data={'tiny_code': ['configs/*', 'styles/*']},
    python_requires='>=3.9',
    install_requires=[
        'textual==0.55.1',
        'textual[syntax]',
        'pyperclip==1.8.2',
    ],
)
