from distutils.core import setup

setup(
    name="attrdict",
    version="0.3.0",
    author="Brendan Curran-Johnson",
    author_email="brendan@bcjbcj.ca",
    packages=["attrdict"],
    url="https://github.com/bcj/AttrDict",
    license="MIT License",
    description="A dict with attribute-style access",
    long_description=open('README.rst').read(),
)
