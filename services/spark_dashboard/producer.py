import random
import os
import json
from datetime import datetime, timedelta
from kafka import KafkaProducer
import time

class ContractRiskDataProducer:
    def __init__(self, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers
        self.producer = self.create_kafka_producer()

    def create_kafka_producer(self):
        return KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
        )

    def generate_contract_data(self):
        # 定义合同类型
        contract_types = [
            "买卖合同",  "赠与合同",
            "借款合同", "保证合同", "租赁合同",
            "承揽合同",  "运输合同","服务合同",
            "技术合同", "保管合同", "仓储合同", "委托合同",
             "行纪合同", "中介合同", "合伙合同"
        ]

        # 随机选择合同类型
        contract_type = random.choice(contract_types)

        # 根据合同类型生成相关条款
        if contract_type == "买卖合同":
            payment_terms = "货到付款"
            deliverables = "商品交付"
        elif contract_type == "租赁合同":
            payment_terms = "按月支付租金"
            deliverables = "租赁物交付"
        elif contract_type == "服务合同":
            payment_terms = "服务完成支付"
            deliverables = "服务完成"
        else:
            payment_terms = "按合同约定支付"
            deliverables = "按合同约定交付"

        contract_data = {
            "contract_name": f"{contract_type}示例",
            "contract_type": contract_type,
            "contract_amount": round(random.uniform(1000, 1000000), 2),
            "payment_terms": payment_terms,
            "performance_period_start": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
            "performance_period_end": (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "deliverables": deliverables,
            "breach_clauses": random.choice(["违约方需支付合同金额的10%作为违约金", "违约方需承担所有损失", "违约方需支付高额违约金"]),
            "dispute_resolution": random.choice(["通过仲裁解决，仲裁机构为北京市仲裁委员会", "通过诉讼解决，管辖法院为合同签订地法院", "通过协商解决，协商不成再仲裁"]),
            "party_a_credit_rating": random.choice(["AAA", "AA", "A", "B", "C"]),
            "party_b_credit_rating": random.choice(["AAA", "AA", "A", "B", "C"]),
            "market_conditions": random.choice(["市场稳定，原材料价格波动小", "市场波动较大，需关注原材料价格", "市场需求旺盛，价格稳定"]),
            "industry_trends": random.choice(["行业增长趋势明显，政策支持", "行业竞争激烈，价格下降", "行业平稳发展，无明显变化"]),
            "customer_id": f"cust-{random.randint(1000, 9999)}"
        }
        return contract_data

    def send_data_to_kafka(self, topic, num_messages):
        for _ in range(num_messages):
            data = self.generate_contract_data()
            self.producer.send(topic, value=data)
            print(f"发送数据: {data}")
            time.sleep(5)  # 每5秒发送一次数据
        self.producer.close()

if __name__ == "__main__":
    # Kafka服务器地址
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    # 创建数据生成器
    producer = ContractRiskDataProducer(bootstrap_servers)

    # 发送10条模拟数据到Kafka主题
    producer.send_data_to_kafka("contract_risk_assessment", 100000000000)