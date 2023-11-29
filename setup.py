from setuptools import setup, find_packages

setup(name='otpsy',

      version='0.0.1',

      url='https://github.com/AlexLietard/OTPsy',

      license='MIT',

      author='Alexandre LIETARD',

      author_email='alex.lietard77@gmail.com',

      description='Packages designed to detect outliers in Psychology',

      packages=find_packages(exclude=['tests']),

      long_description=open('README.md').read(),

      zip_safe=False,

      setup_requires=['nose>=1.0'],

      test_suite='nose.collector')
