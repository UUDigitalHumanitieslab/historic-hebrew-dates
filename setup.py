from setuptools import setup, find_packages

with open('README.rst', encoding='utf-8-sig') as file:
    long_description = file.read()

setup(
    name='historical-hebrew-dates',
    python_requires='>=3.6, <4',
    version='0.0.1',
    description='Extracting historical Hebrew dates from text.',
    long_description=long_description,
    author='Digital Humanities Lab, Utrecht University',
    author_email='digitalhumanities@uu.nl',
    url='https://github.com/UUDigitalHumanitieslab/historic-hebrew-dates',
    license='MIT',
    packages=['historic-hebrew-dates'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'historic-hebrew-dates = historic-hebrew-dates.__main__:main'
        ]
    })
