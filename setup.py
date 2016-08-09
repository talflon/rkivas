from setuptools import setup, find_packages


setup(
    name='rkivas',
    version='0.1',
    packages=find_packages(exclude=['tests', 'env']),
    test_suite='tests',
    install_requires=[
    ],
    setup_requires=[
        'pytest-runner>=2.0,<3',
    ],
    tests_require=[
        'pytest>=2.6.1,<3',
        'hypothesis>=2.0,<4',
    ],
)
