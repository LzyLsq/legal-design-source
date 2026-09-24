// 初始化图表
const riskDistributionChart = echarts.init(document.getElementById('risk-distribution-chart'));
const amountDistributionChart = echarts.init(document.getElementById('amount-distribution-chart'));
const creditRatingChart = echarts.init(document.getElementById('credit-rating-chart'));
const riskTrendChart = echarts.init(document.getElementById('risk-trend-chart'));
const contractTypeChart = echarts.init(document.getElementById('contract-type-chart'));

// 风险分布图表配置
const riskDistributionOption = {
    tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
        orient: 'vertical',
        right: 10,
        top: 'center',
        itemWidth: 14,
        itemHeight: 8
    },
    color: ['#4285F4', '#EA4335', '#FBBC05'], // 蓝色、红色、黄色
    series: [
        {
            name: '合同数量',
            type: 'pie',
            radius: ['45%', '70%'],
            center: ['50%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: {
                show: true,
                formatter: '{b}: {c} ({d}%)',
                fontSize: 13
            },
            emphasis: {
                label: {
                    show: true,
                    fontSize: '14',
                    fontWeight: 'bold'
                }
            },
            labelLine: {
                show: true,
                length: 10,
                length2: 10
            },
            data: []
        }
    ]
};

// 标的额分布图表配置
const amountDistributionOption = {
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'shadow'
        }
    },
    legend: {
        data: ['合同数量'],
        bottom: 10
    },
    grid: {
        left: '3%',
        right: '4%',
        top: '45%',
        bottom: '20%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        data: ['低 (≤10万)', '中 (10万-50万)', '高 (>50万)'],
        axisLabel: {
            fontSize: 13
        },
        axisLine: {
            lineStyle: {
                color: '#999'
            }
        }
    },
    yAxis: {
        type: 'value',
        axisLabel: {
            fontSize: 13
        },
        axisLine: {
            lineStyle: {
                color: '#999'
            }
        },
        splitLine: {
            lineStyle: {
                color: '#eee'
            }
        }
    },
    series: [
        {
            name: '合同数量',
            type: 'bar',
            barWidth: '50%',
            itemStyle: {
                borderRadius: [5, 5, 0, 0]
            },
            data: []
        }
    ]
};

// 信用评级分布图表配置
const creditRatingOption = {
    tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
        orient: 'vertical',
        right: 10,
        top: 'center',
        itemWidth: 14,
        itemHeight: 8
    },
    color: ['#4285F4', '#34A853', '#FBBC05', '#EA4335', '#93216B'], // 蓝色、绿色、黄色、红色、紫色
    series: [
        {
            name: '信用评级',
            type: 'pie',
            radius: ['45%', '70%'],
            center: ['50%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: {
                show: true,
                formatter: '{b}: {c} ({d}%)',
                fontSize: 13
            },
            emphasis: {
                label: {
                    show: true,
                    fontSize: '14',
                    fontWeight: 'bold'
                }
            },
            labelLine: {
                show: true,
                length: 10,
                length2: 10
            },
            data: []
        }
    ]
};

// 风险趋势图表配置
const riskTrendOption = {
    tooltip: {
        trigger: 'axis'
    },
    legend: {
        data: ['低风险', '中风险', '高风险'],
        bottom: 10
    },
    grid: {
        left: '3%',
        right: '4%',
        top: '45%',
        bottom: '20%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        data: [],
        axisLabel: {
            fontSize: 13,
            rotate: 45
        },
        axisLine: {
            lineStyle: {
                color: '#999'
            }
        }
    },
    yAxis: {
        type: 'value',
        axisLabel: {
            fontSize: 13
        },
        axisLine: {
            lineStyle: {
                color: '#999'
            }
        },
        splitLine: {
            lineStyle: {
                color: '#eee'
            }
        }
    },
    series: [
        {
            name: '低风险',
            type: 'line',
            smooth: true,
            lineStyle: {
                width: 4,
                color: '#4285F4', // 蓝色
                type: 'solid' // 实线
            },
            areaStyle: {
                opacity: 0.3,
                color: '#4285F4'
            },
            symbol: 'circle', // 圆形标记点
            symbolSize: 8, // 标记点大小
            data: []
        },
        {
            name: '中风险',
            type: 'line',
            smooth: true,
            lineStyle: {
                width: 4,
                color: '#FBBC05', // 黄色
                type: 'dashed' // 虚线
            },
            areaStyle: {
                opacity: 0.3,
                color: '#FBBC05'
            },
            symbol: 'triangle', // 三角形标记点
            symbolSize: 8,
            data: []
        },
        {
            name: '高风险',
            type: 'line',
            smooth: true,
            lineStyle: {
                width: 4,
                color: '#EA4335', // 红色
                type: 'dotted' // 点划线
            },
            areaStyle: {
                opacity: 0.3,
                color: '#EA4335'
            },
            symbol: 'diamond', // 菱形标记点
            symbolSize: 8,
            data: []
        }
    ]
};

// 合同类型分布图表配置
const contractTypeOption = {
    tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
        orient: 'vertical',
        right: 10,
        top: 'center',
        itemWidth: 14,
        itemHeight: 8
    },
    color: ['#4285F4', '#34A853', '#FBBC05', '#EA4335', '#93216B', '#5F5F5F'], // 多种颜色
    series: [
        {
            name: '合同数量',
            type: 'pie',
            radius: ['45%', '70%'],
            center: ['50%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: {
                show: true,
                formatter: '{b}: {c} ({d}%)',
                fontSize: 13
            },
            emphasis: {
                label: {
                    show: true,
                    fontSize: '14',
                    fontWeight: 'bold'
                }
            },
            labelLine: {
                show: true,
                length: 10,
                length2: 10
            },
            data: []
        }
    ]
};

// 渲染初始图表
riskDistributionChart.setOption(riskDistributionOption);
amountDistributionChart.setOption(amountDistributionOption);
creditRatingChart.setOption(creditRatingOption);
riskTrendChart.setOption(riskTrendOption);
contractTypeChart.setOption(contractTypeOption);

// 获取筛选条件
function getFilters() {
    return {
        timeRange: document.getElementById('time-range').value,
        contractType: document.getElementById('contract-type').value,
        riskLevel: document.getElementById('risk-level').value,
        amountRange: document.getElementById('amount-range').value,
        partyACredit: document.getElementById('party-a-credit').value,
        partyBCredit: document.getElementById('party-b-credit').value
    };
}

// 更新图表数据
function updateCharts() {
    const filters = getFilters();

    // 更新最后更新时间
    const now = new Date();
    const formattedDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
    document.getElementById('last-updated').textContent = formattedDate;

    // 获取数据
    fetch('/api/risk-stats', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(filters),
    })
        .then(response => response.json())
        .then(data => {
            // 更新统计数据
            document.getElementById('total-contracts').textContent = data.total_contracts || 0;
            document.getElementById('total-amount').textContent = (data.total_amount || 0).toFixed(2);
            document.getElementById('high-risk-contracts').textContent = data.risk_distribution['高风险'] || 0;

            // 计算风险指数
            const totalContracts = data.total_contracts || 1;
            const highRiskContracts = data.risk_distribution['高风险'] || 0;
            const riskIndex = Math.round((highRiskContracts / totalContracts) * 100);
            document.getElementById('risk-index').textContent = `${riskIndex}%`;

            // 更新风险分布图表
            const riskDistributionData = [
                { value: data.risk_distribution['低风险'] || 0, name: '低风险' },
                { value: data.risk_distribution['中风险'] || 0, name: '中风险' },
                { value: data.risk_distribution['高风险'] || 0, name: '高风险' }
            ];
            riskDistributionChart.setOption({
                series: [{
                    data: riskDistributionData
                }]
            });

            // 更新标定额分布图表
            amountDistributionChart.setOption({
                series: [{
                    data: [
                        data.amount_distribution['低'] || 0,
                        data.amount_distribution['中'] || 0,
                        data.amount_distribution['高'] || 0
                    ]
                }]
            });

            // 更新信用评级分布图表
            const creditRatingData = [
                { value: data.credit_rating_distribution['AAA'] || 0, name: 'AAA' },
                { value: data.credit_rating_distribution['AA'] || 0, name: 'AA' },
                { value: data.credit_rating_distribution['A'] || 0, name: 'A' },
                { value: data.credit_rating_distribution['B'] || 0, name: 'B' },
                { value: data.credit_rating_distribution['C'] || 0, name: 'C' }
            ];
            creditRatingChart.setOption({
                series: [{
                    data: creditRatingData
                }]
            });

            // 更新风险趋势图表
            fetch('/api/risk-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(filters),
            })
                .then(response => response.json())
                .then(items => {
                    const dateGroups = {};
                    items.forEach(item => {
                        const dateString = item.performance_period_start;
                        const parts = dateString.split(/, | /);
                        const day = parts[1];
                        const month = parts[2];
                        const year = parts[3];
                        const time = parts[4];

                        const monthMap = {
                            Jan: 1, Feb: 2, Mar: 3, Apr: 4, May: 5, Jun: 6,
                            Jul: 7, Aug: 8, Sep: 9, Oct: 10, Nov: 11, Dec: 12
                        };
                        const monthNumber = monthMap[month];

                        const dateKey = `${year}-${monthNumber}`;

                        if (!dateGroups[dateKey]) {
                            dateGroups[dateKey] = { low: 0, medium: 0, high: 0 };
                        }

                        switch (item.risk_level) {
                            case '低风险':
                                dateGroups[dateKey].low += 1;
                                break;
                            case '中风险':
                                dateGroups[dateKey].medium += 1;
                                break;
                            case '高风险':
                                dateGroups[dateKey].high += 1;
                                break;
                        }
                    });

                    const dates = Object.keys(dateGroups).sort();
                    const lowData = dates.map(date => dateGroups[date].low);
                    const mediumData = dates.map(date => dateGroups[date].medium);
                    const highData = dates.map(date => dateGroups[date].high);

                    riskTrendChart.setOption({
                        xAxis: {
                            data: dates
                        },
                        series: [
                            {
                                name: '低风险',
                                type: 'line',
                                data: lowData
                            },
                            {
                                name: '中风险',
                                type: 'line',
                                data: mediumData
                            },
                            {
                                name: '高风险',
                                type: 'line',
                                data: highData
                            }
                        ]
                    });
                });

            // 更新合同类型分布图表
            const contractTypeData = Object.entries(data.contract_type_distribution).map(([name, value]) => ({
                name: name,
                value: value
            }));
            contractTypeChart.setOption({
                series: [{
                    data: contractTypeData
                }]
            });

            // 更新风险排名前十列表
            const rankingList = document.getElementById('ranking-list');
            rankingList.innerHTML = '';

            data.top_contracts.forEach(contract => {
                const li = document.createElement('li');
                li.innerHTML = `
                <span class="ranking-customer-id">${contract.customer_id}</span>
                <span class="ranking-contract-name">${contract.contract_name}</span>
                <span class="ranking-start-date">开始时间: ${contract.performance_period_start}</span>
                <span class="ranking-risk-level ${getRiskClass(contract.risk_level)}">
                  ${contract.risk_level}
                </span>
                <span class="ranking-risk-index">风险指数: ${contract.risk_index}</span>
              `;
                rankingList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error updating charts:', error);
        });
}

// 获取风险等级对应的CSS类名
function getRiskClass(riskLevel) {
    switch (riskLevel) {
        case '低风险':
            return 'low-risk';
        case '中风险':
            return 'medium-risk';
        case '高风险':
            return 'high-risk';
        default:
            return '';
    }
}

// 初始加载数据
updateCharts();

// 重置单个筛选项
function resetFilterItem(filterId) {
    document.getElementById(filterId).value = 'all';
}

// 应用筛选按钮
document.getElementById('apply-filter').addEventListener('click', updateCharts);

// 重置筛选按钮
document.getElementById('reset-filter').addEventListener('click', function() {
    // 重置所有筛选条件
    document.getElementById('time-range').value = 'all';
    document.getElementById('contract-type').value = 'all';
    document.getElementById('risk-level').value = 'all';
    document.getElementById('amount-range').value = 'all';
    document.getElementById('party-a-credit').value = 'all';
    document.getElementById('party-b-credit').value = 'all';

    // 更新图表
    updateCharts();
});

setInterval(updateCharts, 5000);