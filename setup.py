"""
simple-sqlalchemy
-------------
simple-sqlalchemy provides easy and simple query method to access mysql data. It
lets you get or change data in a easy way, especially when you get many conditions and
will get any of them.For example, in a query page.

Links
`````
* `documentation <http://git.ucweb.local/heyu/simple-sqlalchemy>`_
*


"""
try:
    from setuptools import setup
except:
    from distutils.core import setup

"""
    Created by heyu on 2015/10/12
"""

setup(
    name="simple-sqlalchemy",
    version="0.0.1",
    author="heyu",
    author_email="hy99526@alibaba-inc.com",
    description="a simple query tools based on sqlalchemy",
    long_description=__doc__,
    install_requires=["sqlalchemy>=1.0.0b4"],
    url="http://git.ucweb.local/heyu/simple-sqlalchemy",
    packages=["simple"],
    platforms=['all'],
    test_suite="tests"
)
