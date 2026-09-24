import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import db, web  # noqa: E402

from flask import render_template, request, jsonify
from datetime import datetime

app = web.create_flask_app(__name__)

@app.route('/')
def index():
    return render_template('contractData.html')

@app.route('/api/contracts')
def get_contracts():
    # 获取查询参数
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search = request.args.get('search', '')
    contract_type = request.args.get('contract_type', '')
    risk_level = request.args.get('risk_level', '')

    try:
        with db.db_cursor("mysql") as cursor:
                # 基础查询
                query = """
                SELECT
                    contract_name, contract_type, contract_amount,
                    payment_terms, performance_period_start, performance_period_end,
                    deliverables, breach_clauses, dispute_resolution,
                    party_a_credit_rating, party_b_credit_rating,
                    market_conditions, industry_trends, customer_id,
                    risk_index, risk_level
                FROM contract_risk_results
                WHERE 1=1
                """
                params = []

                # 添加搜索条件
                if search:
                    query += " AND (contract_name LIKE %s OR customer_id LIKE %s OR risk_level LIKE %s)"
                    params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

                # 添加合同类型筛选
                if contract_type:
                    query += " AND contract_type = %s"
                    params.append(contract_type)

                # 添加风险等级筛选
                if risk_level:
                    query += " AND risk_level = %s"
                    params.append(risk_level)

                # 获取总数
                count_query = f"SELECT COUNT(*) as total FROM ({query}) as t"
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']

                # 添加分页
                query += " LIMIT %s OFFSET %s"
                params.extend([per_page, (page - 1) * per_page])

                # 执行查询
                cursor.execute(query, params)
                contracts = cursor.fetchall()

                # 格式化日期字段
                for contract in contracts:
                    for field in ['performance_period_start', 'performance_period_end']:
                        if contract[field] and isinstance(contract[field], datetime):
                            contract[field] = contract[field].strftime('%Y-%m-%d')

                return jsonify({
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'data': contracts
                })

    except Exception:  # noqa: BLE001
        app.logger.exception("查询合同数据失败")
        return jsonify({'error': '服务端错误，请稍后重试'}), 500


if __name__ == '__main__':
    web.run_flask(app, 5010)
