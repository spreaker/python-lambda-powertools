from setuptools import find_packages, setup
setup(
    name='lambda_powertools',
    packages=find_packages(include=['lambda_powertools']),
    version='0.2.0',
    description='Lambda Powertools is a package encapsulating utilities and best practices used to write Python Lambda functions at Spreaker.',
    author='Spreaker',
    license='MIT',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==7.2.2', 'pytest-mock==3.10.0'],
    test_suite='tests'
)
