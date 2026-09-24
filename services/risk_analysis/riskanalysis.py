import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import db, web  # noqa: E402

from flask import render_template, request, redirect, url_for, session
from datetime import datetime

app = web.create_flask_app(__name__)


def calculate_risk_score(data):
    """计算风险评分"""
    # 定义权重
    weights = {
        "amount_score": 0.2,
        "payment_score": 0.1,
        "performance_score": 0.1,
        "deliverables_score": 0.1,
        "breach_score": 0.1,
        "dispute_score": 0.1,
        "party_a_score": 0.1,
        "party_b_score": 0.1,
        "market_score": 0.05,
        "industry_score": 0.05
    }

    # 初始化分数
    scores = {key: 0.0 for key in weights.keys()}

    # 合同金额
    if data['contract_amount'] > 1000000:
        scores["amount_score"] = 5.0
    elif data['contract_amount'] > 500000:
        scores["amount_score"] = 4.0
    elif data['contract_amount'] > 100000:
        scores["amount_score"] = 3.0
    elif data['contract_amount'] > 50000:
        scores["amount_score"] = 2.0
    else:
        scores["amount_score"] = 1.0

    # 付款方式
    if data['payment_terms'] == "预付款":
        scores["payment_score"] = 2.0
    elif data['payment_terms'] == "分期付款":
        scores["payment_score"] = 3.0
    else:
        scores["payment_score"] = 4.0

    # 履行期限
    start_date = datetime.strptime(data['performance_period_start'], "%Y-%m-%d")
    end_date = datetime.strptime(data['performance_period_end'], "%Y-%m-%d")
    delta = (end_date - start_date).days
    if delta > 365:
        scores["performance_score"] = 5.0
    elif delta > 180:
        scores["performance_score"] = 4.0
    elif delta > 90:
        scores["performance_score"] = 3.0
    elif delta > 30:
        scores["performance_score"] = 2.0
    else:
        scores["performance_score"] = 1.0

    # 交付物或服务内容
    if data['deliverables_complexity'] == "复杂":
        scores["deliverables_score"] = 5.0
    elif data['deliverables_complexity'] == "中等":
        scores["deliverables_score"] = 3.0
    else:
        scores["deliverables_score"] = 2.0

    # 违约责任
    if data['breach_clauses'] == "高额违约金":
        scores["breach_score"] = 5.0
    elif data['breach_clauses'] == "中等违约金":
        scores["breach_score"] = 3.0
    else:
        scores["breach_score"] = 2.0

    # 争议解决方式
    if data['dispute_resolution'] == "仲裁":
        scores["dispute_score"] = 3.0
    elif data['dispute_resolution'] == "诉讼":
        scores["dispute_score"] = 4.0
    else:
        scores["dispute_score"] = 5.0

    # 信用评级
    if data['party_a_credit_rating'] == "AAA":
        scores["party_a_score"] = 1.0
    elif data['party_a_credit_rating'] == "AA":
        scores["party_a_score"] = 2.0
    elif data['party_a_credit_rating'] == "A":
        scores["party_a_score"] = 3.0
    elif data['party_a_credit_rating'] == "B":
        scores["party_a_score"] = 4.0
    else:
        scores["party_a_score"] = 5.0

    if data['party_b_credit_rating'] == "AAA":
        scores["party_b_score"] = 1.0
    elif data['party_b_credit_rating'] == "AA":
        scores["party_b_score"] = 2.0
    elif data['party_b_credit_rating'] == "A":
        scores["party_b_score"] = 3.0
    elif data['party_b_credit_rating'] == "B":
        scores["party_b_score"] = 4.0
    else:
        scores["party_b_score"] = 5.0

    # 市场行情
    if data['market_conditions'] == "不稳定":
        scores["market_score"] = 5.0
    elif data['market_conditions'] == "波动":
        scores["market_score"] = 4.0
    else:
        scores["market_score"] = 3.0

    # 行业趋势
    if data['industry_trends'] == "下降":
        scores["industry_score"] = 5.0
    elif data['industry_trends'] == "平稳":
        scores["industry_score"] = 3.0
    else:
        scores["industry_score"] = 2.0

    # 计算风险指数
    risk_index = sum(scores[key] * weights[key] for key in weights.keys())

    return risk_index

def save_to_database(data, risk_index, risk_level):
    """将数据存储到数据库"""
    sql = """
        INSERT INTO contract_risk_results
        (contract_name, contract_type, contract_amount, payment_terms, performance_period_start,
         performance_period_end, deliverables, breach_clauses, dispute_resolution,
         party_a_credit_rating, party_b_credit_rating, market_conditions, industry_trends,
         customer_id, risk_index, risk_level)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        data['contract_name'],
        data['contract_type'],
        data['contract_amount'],
        data['payment_terms'],
        data['performance_period_start'],
        data['performance_period_end'],
        data['deliverables'],
        data['breach_clauses'],
        data['dispute_resolution'],
        data['party_a_credit_rating'],
        data['party_b_credit_rating'],
        data['market_conditions'],
        data['industry_trends'],
        data['customer_id'],
        risk_index,
        risk_level,
    )
    try:
        with db.db_cursor("pymysql", commit=True, dictionary=False) as cursor:
            cursor.execute(sql, values)
    except Exception:  # noqa: BLE001
        app.logger.exception("保存合同风险结果失败")
        return False
    return True


@app.route('/')
def index():
    """渲染表单页面"""
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    """处理表单提交"""
    data = {
        "contract_name": request.form['contract_name'],
        "contract_type": request.form['contract_type'],
        "contract_amount": float(request.form['contract_amount']),
        "payment_terms": request.form['payment_terms'],
        "performance_period_start": request.form['performance_period_start'],
        "performance_period_end": request.form['performance_period_end'],
        "deliverables": request.form['deliverables'],
        "deliverables_complexity": request.form['deliverables_complexity'],
        "breach_clauses": request.form['breach_clauses'],
        "dispute_resolution": request.form['dispute_resolution'],
        "party_a_credit_rating": request.form['party_a_credit_rating'],
        "party_b_credit_rating": request.form['party_b_credit_rating'],
        "market_conditions": request.form['market_conditions'],
        "industry_trends": request.form['industry_trends'],
        "customer_id": request.form['customer_id']
    }

    # 计算风险指数
    risk_index = calculate_risk_score(data)

    # 确定风险等级
    if risk_index <= 3.2:
        risk_level = "低风险"
    elif risk_index <= 3.6:
        risk_level = "中风险"
    else:
        risk_level = "高风险"

    # 将风险指数和等级存储到session中，以便在结果页面显示
    session['risk_index'] = risk_index
    session['risk_level'] = risk_level

    app.logger.info("风险评估结果：风险指数=%s，风险等级=%s", risk_index, risk_level)
    app.logger.debug("待写入字段：%s", {**data, "risk_index": risk_index, "risk_level": risk_level})

    # 保存到数据库
    if save_to_database(data, risk_index, risk_level):
        return redirect(url_for('result'))
    else:
        return redirect(url_for('error'))

@app.route('/result')
def result():
    """显示风险评估结果"""
    return render_template('result.html')

@app.route('/error')
def error():
    """提交失败页面"""
    return render_template('error.html')

if __name__ == '__main__':
    web.run_flask(app, 5020)
