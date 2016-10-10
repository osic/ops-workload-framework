from setuptools import setup

setup(
    name='click-example-validation',
    version='1.0',
    py_modules=['workload_def'],
    include_package_data=True,
    install_requires=[
        'click',
        'python-openstackclient'
    ],
    entry_points='''
        [console_scripts]
        workload_def=workload_def:workload_def
    ''',
)
