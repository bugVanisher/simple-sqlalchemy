simple-sqlalchemy

simple-sqlalchemy provides easy and simple query methods to access mysql data. It
lets you get or change data in a easy way, especially when you get many conditions and
will get any of them.For example, in a query page.

firstly, execute 'source ddl.sql' in your mysql server
then
take a look at the file /tests/abstractquery_test.py then change it according to your mysql
configuration and then try 'python setup.py test' to  run the unit tests

or 
you can run 'python setup.py sdist' to make a zip (on windows) or tar.gz (on linux) 
then unzip it and run 'python setup.py install'  to  install simple-sqlalchemy on your machine.