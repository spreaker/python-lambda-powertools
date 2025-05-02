from setuptools import find_packages, setup
setup(
    name='lambda_powertools',
    packages=find_packages(include=['lambda_powertools']),
    version='0.2.1',
    description='Lambda Powertools is a package encapsulating utilities and best practices used to write Python Lambda functions at Spreaker.',
    author='Spreaker',
    license='MIT',
    install_requires=['prometheus-client==0.21.1'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==8.3.5', 'pytest-mock==3.14.0'],
    test_suite='tests'
)
