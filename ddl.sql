set names utf8;

CREATE DATABASE simple_demo;


USE simple_demo;

CREATE TABLE `charge_record` (
  `charge_record_id` bigint(20) NOT NULL COMMENT '充值记录id',
  `out_bill_no` bigint(20) NOT NULL COMMENT '外部充值订单号',
  `order_no` bigint(20) NOT NULL COMMENT '订单号',
  `charge_status` smallint(6) NOT NULL COMMENT '充值状态,1:充值中,2:充值成功,3:充值失败',
  `message` varchar(100) COLLATE utf8_bin DEFAULT NULL COMMENT '充值失败原因',
  `finish_time` int(11) DEFAULT NULL,
  `ctime` int(11) NOT NULL,
  `utime` int(11) NOT NULL,
  PRIMARY KEY (`charge_record_id`),
  KEY `idx_order_no` (`order_no`),
  KEY `idx_status_ctime` (`charge_status`,`ctime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='充值记录';

