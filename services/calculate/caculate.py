import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import web  # noqa: E402

from flask import render_template, request, jsonify
from functools import lru_cache

app = web.create_flask_app(__name__)

# 获取最新LPR（示例数据，实际应从权威API获取）
@lru_cache(maxsize=1)
def get_latest_lpr():
    try:
        # 模拟返回最新LPR
        return 3.7
    except Exception as e:
        print(f"获取LPR失败: {e}")
        return None

# 利息计算（依据：《中华人民共和国民法典》第六百七十六条）
def calculate_interest(principal, rate, period):
    return principal * (rate / 100) * period

# 违约金计算（依据：《中华人民共和国民法典》第五百八十五条）
def calculate_liquidated_damages(principal, breach_rate):
    return principal * (breach_rate / 100)

# 诉讼费计算（依据：《诉讼费用交纳办法》（国务院令第481号））
def calculate_lawsuit_fee(amount):
    if amount <= 10000:
        return amount * 0.025 + 200
    elif 10000 < amount <= 200000:
        return amount * 0.02 + 210
    elif 200000 < amount <= 500000:
        return amount * 0.015 + 2110
    elif 500000 < amount <= 1000000:
        return amount * 0.01 + 5110
    elif 1000000 < amount <= 2000000:
        return amount * 0.0095 + 10110
    elif 2000000 < amount <= 5000000:
        return amount * 0.009 + 19110
    elif 5000000 < amount <= 10000000:
        return amount * 0.0085 + 44110
    else:
        return amount * 0.008 + 84110

# 迟延履行期间的债务利息计算（依据：《中华人民共和国民事诉讼法》第二百六十条）
def calculate_delayed_interest(principal, delay_days):
    daily_rate = 5.775 / 365 / 100  # 假设年利率为5.775%
    return principal * daily_rate * delay_days

# 执行费计算（依据：《诉讼费用交纳办法》（国务院令第481号））
def calculate_execution_fee(amount):
    if amount <= 10000:
        return amount * 0.01 + 200
    elif 10000 < amount <= 500000:
        return amount * 0.005 + 2200
    elif 500000 < amount <= 5000000:
        return amount * 0.001 + 27200
    elif 5000000 < amount <= 10000000:
        return amount * 0.0005 + 52200
    else:
        return amount * 0.0001 + 77200

# 财产保全费计算（依据：《诉讼费用交纳办法》（国务院令第481号））
def calculate_preservation_fee(amount):
    if amount <= 10000:
        return 30
    elif 10000 < amount <= 1000000:
        return amount * 0.001 + 20
    else:
        return 2020

# 赔偿金计算（依据：《中华人民共和国民法典》第一千一百七十九条）
def calculate_compensation(actual_loss, mental_damage):
    return actual_loss + mental_damage

# 抚养费计算（依据：《中华人民共和国民法典》第一千零六十七条）
def calculate_child_support(income, children=1):
    rate = 0.25  # 平均按25%计算
    return income * rate / 12 * children

# 合同定金罚则计算（依据：《中华人民共和国民法典》第五百八十六条、第五百八十七条）
def calculate_deposit_penalty(deposit_amount):
    return deposit_amount * 2

# 工伤赔偿计算
def calculate_work_injury(injury_level, monthly_salary):
    # 根据工伤等级计算赔偿月数（示例数据，实际应根据法律法规调整）
    compensation_months = [27, 25, 23, 21, 18, 16, 13, 11, 9, 7]
    if 1 <= injury_level <= 10:
        return monthly_salary * compensation_months[injury_level - 1]
    else:
        raise ValueError("无效的工伤等级")

# 交通事故赔偿计算
def calculate_traffic_accident(liability_percentage, total_loss):
    return total_loss * (liability_percentage / 100)

# 知识产权赔偿计算
def calculate_intellectual_property(infringement_profit, rights_cost):
    return max(infringement_profit, rights_cost)  # 简化计算，实际应更复杂

# 公司解散清算费用计算
def calculate_company_liquidation(total_assets, total_liabilities):
    return total_assets - total_liabilities

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    calculation_type = data.get('type')
    params = data.get('params', {})

    if not params:
        return jsonify({'error': '缺少参数'}), 400

    result = None
    error = None

    try:
        if calculation_type == 'interest':
            principal = float(params.get('principal', 0))
            rate = float(params.get('rate', 0))
            period = float(params.get('period', 0))
            result = calculate_interest(principal, rate, period)
        elif calculation_type == 'liquidated_damages':
            principal = float(params.get('principal', 0))
            breach_rate = float(params.get('breach_rate', 0))
            result = calculate_liquidated_damages(principal, breach_rate)
        elif calculation_type == 'lawsuit_fee':
            amount = float(params.get('amount', 0))
            result = calculate_lawsuit_fee(amount)
        elif calculation_type == 'delayed_interest':
            principal = float(params.get('principal', 0))
            delay_days = float(params.get('delay_days', 0))
            result = calculate_delayed_interest(principal, delay_days)
        elif calculation_type == 'execution_fee':
            amount = float(params.get('amount', 0))
            result = calculate_execution_fee(amount)
        elif calculation_type == 'preservation_fee':
            amount = float(params.get('amount', 0))
            result = calculate_preservation_fee(amount)
        elif calculation_type == 'compensation':
            actual_loss = float(params.get('actual_loss', 0))
            mental_damage = float(params.get('mental_damage', 0))
            result = calculate_compensation(actual_loss, mental_damage)
        elif calculation_type == 'child_support':
            income = float(params.get('income', 0))
            children = int(params.get('children', 1))
            result = calculate_child_support(income, children)
        elif calculation_type == 'deposit_penalty':
            deposit_amount = float(params.get('deposit_amount', 0))
            result = calculate_deposit_penalty(deposit_amount)
        elif calculation_type == 'work_injury':
            injury_level = int(params.get('injury_level', 1))
            monthly_salary = float(params.get('monthly_salary', 0))
            result = calculate_work_injury(injury_level, monthly_salary)
        elif calculation_type == 'traffic_accident':
            liability_percentage = float(params.get('liability_percentage', 0))
            total_loss = float(params.get('total_loss', 0))
            result = calculate_traffic_accident(liability_percentage, total_loss)
        elif calculation_type == 'intellectual_property':
            infringement_profit = float(params.get('infringement_profit', 0))
            rights_cost = float(params.get('rights_cost', 0))
            result = calculate_intellectual_property(infringement_profit, rights_cost)
        elif calculation_type == 'company_liquidation':
            total_assets = float(params.get('total_assets', 0))
            total_liabilities = float(params.get('total_liabilities', 0))
            result = calculate_company_liquidation(total_assets, total_liabilities)
        else:
            error = '未知的计算类型'
    except Exception as e:
        error = str(e)
        app.logger.error(f"计算失败: {str(e)}")

    response_data = {
        'result': round(result, 2) if result is not None else None,
        'error': error
    }

    return jsonify(response_data)

@app.route('/get_lpr')
def get_lpr():
    lpr = get_latest_lpr()
    if lpr is None:
        return jsonify({'error': '获取LPR失败'}), 500
    return jsonify({'lpr': lpr})

if __name__ == '__main__':
    web.run_flask(app, 5007)