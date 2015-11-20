#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import time
from sqlalchemy import Column, BIGINT, VARCHAR, INT, SMALLINT
from sqlalchemy.ext.declarative import declarative_base
from simple.abstractquery import *

"""
    Created by heyu on 2015/10/12
"""
BaseDDL = declarative_base()
SessionFactory.set_debug(False)


class ChargeRecord(BaseDDL):
    '''
        charge_record ddl
    '''
    __tablename__ = 'charge_record'

    charge_record_id = Column(BIGINT(), primary_key=True)
    out_bill_no = Column(BIGINT())
    order_no = Column(BIGINT())
    charge_status = Column(SMALLINT())
    message = Column(VARCHAR(100))
    finish_time = Column(INT())
    ctime = Column(INT())
    utime = Column(INT())

    def __repr__(self):
        return "<charge_record:charge_record_id={charge_record_id},out_bill_no={out_bill_no}," \
               "order_no={orderno},charge_status={cs},message={message},finish_time={ftime}," \
               "ctime={ctime},utime={utime}>".format(
            charge_record_id=self.charge_record_id, out_bill_no=self.out_bill_no, orderno=self.order_no,
            cs=self.charge_status, message=self.message, ftime=self.finish_time, ctime=self.ctime, utime=self.utime)


class ChargeRecordQuery(BaseQuery):
    charge_record_ids = None
    out_bill_no = None
    order_no = None
    charge_status = None
    sfinish_time = None
    efinish_time = None

    @BindAttrField(ChargeRecord.charge_record_id, OperateType.IN, JoinType.AND_JOIN)
    def set_charge_record_ids(self, value):
        self.charge_record_ids = value

    @BindAttrField(ChargeRecord.charge_record_id, OperateType.EQUALS, JoinType.AND_JOIN)
    def set_charge_record_id(self, value):
        self.charge_record_ids = value

    @BindAttrField(ChargeRecord.out_bill_no, OperateType.EQUALS, JoinType.AND_JOIN)
    def set_out_bill_no(self, value):
        self.out_bill_no = value

    @BindAttrField(ChargeRecord.order_no, OperateType.EQUALS, JoinType.AND_JOIN)
    def set_order_no(self, value):
        self.order_no = value

    @BindAttrField(ChargeRecord.charge_status, OperateType.EQUALS, JoinType.AND_JOIN)
    def set_charge_status(self, value):
        self.charge_status = value

    @BindAttrField(ChargeRecord.finish_time, OperateType.LARGER_AND_EQUALS, JoinType.AND_JOIN)
    def set_sftime(self, value):
        self.sfinish_time = value

    @BindAttrField(ChargeRecord.finish_time, OperateType.LESS_AND_EQUALS, JoinType.AND_JOIN)
    def set_eftime(self, value):
        self.efinish_time = value

    @BindAttrField(ChargeRecord.ctime, OperateType.LESS_AND_EQUALS, JoinType.AND_JOIN)
    def set_ectime(self, value):
        self.efinish_time = value


class Tests(unittest.TestCase):
    basedao = Dal(DBConfig(host="127.0.0.1", port=3306, user="", pwd="", db="simple_demo"))

    @classmethod
    def setUpClass(cls):
        print("start")

    def setUp(self):
        self.now = int(time.time())
        record1 = ChargeRecord(
            charge_record_id=1419496454297216,
            out_bill_no=361449596,
            order_no=1419489665114086,
            charge_status=2,
            ctime=self.now,
            utime=self.now
        )

        record2 = ChargeRecord(
            charge_record_id=1419496454297217,
            out_bill_no=361449196,
            order_no=1419489665114084,
            charge_status=2,
            ctime=self.now,
            utime=self.now
        )
        record3 = ChargeRecord()

        record3.charge_record_id = 1419496454297218
        record3.out_bill_no = 361449592
        record3.order_no = 1419489645114086
        record3.charge_status = 2
        record3.ctime = self.now
        record3.utime = self.now

        self.re1 = record1
        self.re2 = record2
        self.re3 = record3

        self._test_add_records()

    def tearDown(self):
        self._test_delete_records()
        del self.re1, self.re2, self.re3

    @classmethod
    def tearDownClass(cls):
        cls.basedao.close()
        print("end")

    def _test_add_records(self):
        self.basedao.batch_save([self.re1, self.re2])
        self.basedao.save(self.re3)

    def _test_delete_records(self):
        query = ChargeRecordQuery()
        query.set_charge_record_ids([1419496454297216, 1419496454297217, 1419496454297218])
        self.basedao.delete(ChargeRecord, query)

    def test_get_records(self):
        query = ChargeRecordQuery()
        query.set_charge_record_id(1419496454297218)
        results = self.basedao.get_list(ChargeRecord, query)
        self.assertEqual(len(results), 1)
        self.assertIn(self.re3, results)

        query2 = ChargeRecordQuery()

        query2.set_charge_status(2)
        query2.set_ectime(self.now + 1000)
        count = self.basedao.count(ChargeRecord.charge_record_id, query2)
        self.assertEqual(count[0], 3)

        query2.set_page(1)
        query2.set_count(10)
        results = self.basedao.get_list(ChargeRecord, query2)
        self.assertEqual(len(results), 3)
        self.assertIn(self.re1, results)
        self.assertIn(self.re2, results)
        self.assertIn(self.re3, results)

    def test_update_record(self):
        update = {
            ChargeRecord.charge_status: 3,
            ChargeRecord.finish_time: self.now + 10,
            ChargeRecord.utime: self.now + 10
        }
        query = ChargeRecordQuery()
        query.set_charge_record_ids([1419496454297218])
        self.basedao.update(ChargeRecord, update, query)
        charge_record = self.basedao.get(1419496454297218, ChargeRecord)[0]
        self.assertEqual(charge_record.charge_status, 3)
        self.assertEqual(charge_record.finish_time, self.now + 10)
        self.assertEqual(charge_record.utime, self.now + 10)


if __name__ == '__main__':
    # 执行前更改下Tests.basedao为具体的数据库配置
    unittest.main()
