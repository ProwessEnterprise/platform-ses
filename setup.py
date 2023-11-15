from setuptools import setup, find_packages

setup(
    name='simple-email-service',
    package_dir={'': 'app'},
    packages=find_packages(where='app'),
    python_requires=">=3.8",
    # install_requires=['tornado'],
    # test_suite='tests',
)
