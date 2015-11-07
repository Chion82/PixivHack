from setuptools import setup
setup(
  name = 'pixivhack',
  packages = ['pixivhack'],
  entry_points={
      'console_scripts': [
          'pixivhack = pixivhack.pixivhack:main',
      ],
  },
  install_requires=['requests'],
  version = '0.1.5',
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
  ]
)
