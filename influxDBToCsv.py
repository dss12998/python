#!/usr/bin/python
from influxdb import InfluxDBClient
import time
import csv


def influxDBToCsv():
    try:
        # 连接influxDB
        client = InfluxDBClient(
            host='主机地址',
            port=端口号,
            username='用户名',
            password='密码',
            ssl=True,  # 开启ssl
            verify_ssl=False,
            timeout=30,
        )
    except Exception as e:
        print(e)
    else:
        # 切换数据库
        client.switch_database('数据库')

        # 查询语句
        sql = """
    SELECT last("p95") AS "last", mean("p95") AS "avg", max("p95") AS "max" FROM "application.httprequests__transactions_per_endpoint" WHERE ("env" = 'release' AND "app" = 'Lunz.Web.ServicePlatform.Api' AND time >= now()-1d AND time <= now()) GROUP BY "route"
    """
        # 收集时间
        acq_time = time.strftime('%Y-%m-%d %X', time.localtime())

        # 定义列表
        result_list = []

        # 处理结果集
        resultSet = client.query(query=sql).items()
        for result in resultSet:
            route = result[0][1]
            for r in result[1]:
                del r['time']
                route.update(r)
                route['time'] = acq_time
                result_list.append(route)

        # 写入csv
        header = ['route', 'last', 'avg', 'max', 'time']
        with open('response_time.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(result_list)

        # 关闭数据库连接
        client.close()


if __name__ == '__main__':
    try:
        influxDBToCsv()
    except Exception as e:
        print(e)
    else:
        logTime = time.strftime('%Y-%m-%d %X', time.localtime())
        print(logTime + "  数据写入成功！")

