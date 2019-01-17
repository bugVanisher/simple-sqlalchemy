## simple-sqlalchemy

simple-sqlalchemy provides easy and simple query methods to access mysql data. It
lets you get or change data in an easy way, especially when you get many conditions and
will get any of them.For example, in a query page.

### Test it locally
    step 1: source ddl.sql;
    step 2: export db_user="{you db user}" && export db_pass="{you db password}";
    step 3: python -m tests.abstractquery_test;