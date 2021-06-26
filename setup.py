from setuptools import setup

setup(name='vvvacinabot',
      version='0.1',
      description='Fetch vacines vacancies',
      url='git@github.com:mikaelhadler/vvvacinasbot.git',
      author='Gustavo RPS, Mikael Hadler',
      author_email='gustavorps@argocrew.io, mikaelhadler@gmail.com',
      license='MIT',
      packages=['vacinebot'],
      install_requires=[
          'telegram'
      ],
      include_package_data=True,
      zip_safe=False)