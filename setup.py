from cx_Freeze import setup, Executable

build_options = {
    'packages': ['pandas', 'numpy', 'pytz', 'dateutil'],
    'includes': [],
    'excludes': [],
}

setup(
    name='YourAppName',
    version='1.0',
    description='My Application',
    options={'build_exe': build_options},
    executables=[Executable('app.py')]
)