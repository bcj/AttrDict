from distutils.core import setup

setup(
    name="attrdict",
    version="0.2.0",
    author="Brendan Curran-Johnson",
    author_email="brendan@bcjbcj.ca",
    packages=["attrdict", "attrdict.test"],
    url="https://github.com/bcj/AttrDict",
    license="LICENSE.txt",
    description="A dict with attribute-style access",
    long_description=open('README.rst').read(),
)
