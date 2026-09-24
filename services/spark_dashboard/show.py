import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import db, web  # noqa: E402

from flask import render_template, jsonify, request
from datetime import datetime, timedelta


app = web.create_flask_app(__name__)


def fetch_risk_data(filters=None):
    """从MySQL数据库中获取合同风险数据"""
    sql = """
        SELECT
            contract_name, contract_type, contract_amount, payment_terms,
            performance_period_start, performance_period_end,
            deliverables, breach_clauses, dispute_resolution,
            party_a_credit_rating, party_b_credit_rating,
            market_conditions, industry_trends, risk_index, risk_level,
            customer_id
        FROM contract_risk_results
    """

    conditions = []
    params = []
    if filters:
        time_range = filters.get('timeRange', 'all')
        if time_range != 'all':
            conditions.append("performance_period_start >= %s")
            params.append(datetime.now() - timedelta(days=_TIME_RANGE_DAYS.get(time_range, 0)))

        if filters.get('contractType', 'all') != 'all':
            conditions.append("contract_type = %s")
            params.append(filters['contractType'])

        if filters.get('riskLevel', 'all') != 'all':
            conditions.append("risk_level = %s")
            params.append(filters['riskLevel'])

        amount_range = filters.get('amountRange', 'all')
        if amount_range in _AMOUNT_RANGE_SQL:
            conditions.append(_AMOUNT_RANGE_SQL[amount_range])

        if filters.get('partyACredit', 'all') != 'all':
            conditions.append("party_a_credit_rating = %s")
            params.append(filters['partyACredit'])

        if filters.get('partyBCredit', 'all') != 'all':
            conditions.append("party_b_credit_rating = %s")
            params.append(filters['partyBCredit'])

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    try:
        with db.db_cursor("pymysql") as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    except Exception:  # noqa: BLE001
        app.logger.exception("查询合同风险数据失败")
        return []

#: 时间范围 -> 往前推的天数（'custom' 由前端另行提供参数，暂不构造条件）
_TIME_RANGE_DAYS = {"7days": 7, "30days": 30, "90days": 90, "1year": 365}

#: 金额区间 -> SQL 片段（全部是常量，不含用户输入）
_AMOUNT_RANGE_SQL = {
    "low": "contract_amount <= 100000",
    "medium": "contract_amount > 100000 AND contract_amount <= 500000",
    "high": "contract_amount > 500000",
}


def calculate_risk_statistics(data):
    """计算风险统计数据"""
    if not data:
        return {
            'total_contracts': 0,
            'total_amount': 0.0,
            'risk_distribution': {'低风险': 0, '中风险': 0, '高风险': 0},
            'amount_distribution': {'低': 0, '中': 0, '高': 0},
            'credit_rating_distribution': {'AAA': 0, 'AA': 0, 'A': 0, 'B': 0, 'C': 0},
            'contract_type_distribution': {}
        }

    total_contracts = len(data)
    total_amount = sum(float(item['contract_amount']) for item in data)

    # 风险分布
    risk_distribution = {'低风险': 0, '中风险': 0, '高风险': 0}
    for item in data:
        risk_distribution[item['risk_level']] += 1

    # 金额分布
    amount_distribution = {'低': 0, '中': 0, '高': 0}
    for item in data:
        if item['contract_amount'] <= 100000:
            amount_distribution['低'] += 1
        elif item['contract_amount'] <= 500000:
            amount_distribution['中'] += 1
        else:
            amount_distribution['高'] += 1

    # 信用评级分布
    credit_rating_distribution = {'AAA': 0, 'AA': 0, 'A': 0, 'B': 0, 'C': 0}
    for item in data:
        credit_rating_distribution[item['party_a_credit_rating']] += 1
        credit_rating_distribution[item['party_b_credit_rating']] += 1

    # 合同类型分布
    contract_type_distribution = {}
    for item in data:
        contract_type = item['contract_type']
        if contract_type in contract_type_distribution:
            contract_type_distribution[contract_type] += 1
        else:
            contract_type_distribution[contract_type] = 1

    return {
        'total_contracts': total_contracts,
        'total_amount': total_amount,
        'risk_distribution': risk_distribution,
        'amount_distribution': amount_distribution,
        'credit_rating_distribution': credit_rating_distribution,
        'contract_type_distribution': contract_type_distribution
    }

def get_top_risk_contracts(data):
    """获取风险排名前十的合同"""
    if not data:
        return []

    # 按风险指数降序排序，并取前十条
    sorted_data = sorted(data, key=lambda x: x['risk_index'], reverse=True)
    top_10 = sorted_data[:10]

    return top_10

@app.route('/')
def index():
    """渲染前端页面"""
    return render_template('dashboard.html')

@app.route('/api/risk-data', methods=['GET', 'POST'])
def risk_data():
    """提供风险数据的API接口"""
    filters = request.get_json() if request.is_json else request.args.to_dict()
    data = fetch_risk_data(filters)
    return jsonify(data)

@app.route('/api/risk-stats', methods=['GET', 'POST'])
def risk_stats():
    """提供风险统计数据的API接口"""
    filters = request.get_json() if request.is_json else request.args.to_dict()
    data = fetch_risk_data(filters)
    stats = calculate_risk_statistics(data)
    top_contracts = get_top_risk_contracts(data)
    stats['top_contracts'] = top_contracts
    return jsonify(stats)

if __name__ == '__main__':
    web.run_flask(app, 5008)