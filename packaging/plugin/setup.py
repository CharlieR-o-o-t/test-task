from setuptools import setup, find_packages

VERSION = "0.1.dev0"

install_requires = [
    "BeautifulSoup>=3.2.1",
    "boto3>=1.4.4,<1.5.0",
    "djangorestframework==3.9.1",
    "mistune>0.7,<0.9",
    "python-dateutil>=2.0.0,<3.0.0",
    "PyJWT>=1.5.0,<1.6.0",
    "requests-oauthlib==0.3.3",
    "unidiff>=0.5.4",
    # below this line are sentry-plugins specific dependencies
    "cached-property",
    "phabricator>=0.6.0,<1.0",
    "sentry_plugins",
]

setup(name='sentryflo',
      version=VERSION,
      description='Sentry plugin to forward events via SNS',
      url='TODO:',
      author='Siarhei Rasiukevich',
      author_email='me.sudo.su@gmail.com',
      license='Apache',
      #packages=find_packages("src"),
      packages=["sentryflo", "sentryflo.amazon_sns"],
      install_requires=install_requires,
      entry_points={
          'sentry.plugins': [
              'sentry_sns = sentryflo.amazon_sns.plugin:AmazonSNSPlugin'
          ]
      },
      zip_safe=False)