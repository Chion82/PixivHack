from setuptools import setup
setup(
  name = 'pixivhack',
  packages = ['pixivhack'],
  version = '0.1.3',
  description = 'Pixiv Hack is a tool to automatically crawl illustrations filtered by ratings on www.pixiv.net',
  author = 'Chion82',
  license='MIT',
  author_email = 'sdspeedonion@gmail.com',
  url = 'https://github.com/Chion82/PixivHack',
  keywords = ['pixiv', 'pixivhack', 'crawler', 'crawl'],
  classifiers = [
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
  ],
  install_requires=['requests'],
  entry_points={
      'console_scripts': [
          'paxivhack=pixivhack.__main__:main',
      ],
  },
)
