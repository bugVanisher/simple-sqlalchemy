#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
    Created by heyu on 2015/10/13
"""

import unittest
import abstractquery_test


def my_module_suite():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(abstractquery_test)
    return suite
