#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报三维度分析 - 财务数据可视化工具
生成收入和利润的趋势图（PNG + HTML）

用法:
    python3 visualize_trends.py <input_json> <output_dir>

输入 JSON 格式:
{
    "company": "公司名称",
    "revenue": [{"period": "2023Q1", "value": 数值}, ...],
    "profit": [{"period": "2023Q1", "value": 数值}, ...]
}

输出:
    - output_dir/<company>_trends.png (静态图)
    - output_dir/<company>_trends.html (交互图)
    - stdout: {"static_chart": "...", "interactive_chart": "..."}
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

def setup_chinese_font():
    """配置中文字体支持"""
    import matplotlib
    matplotlib.use('Agg')  # 非交互式后端
    
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    
    # 尝试常见的中文字体
    chinese_fonts = [
        'Arial Unicode MS',
        'PingFang SC',
        'Heiti SC',
        'STHeiti',
        'Microsoft YaHei',
        'SimHei',
        'WenQuanYi Micro Hei',
    ]
    
    for font in chinese_fonts:
        try:
            rcParams['font.sans-serif'] = [font]
            rcParams['axes.unicode_minus'] = False
            # 测试是否能正常渲染
            plt.figure()
            plt.text(0.5, 0.5, '测试中文', fontsize=12)
            plt.close()
            print(f"✅ 使用中文字体: {font}")
            return True
        except Exception:
            continue
    
    # 如果都不行，使用默认字体并警告
    print("⚠️  未找到合适的中文字体，图表中的中文可能显示异常")
    rcParams['font.sans-serif'] = ['DejaVu Sans']
    rcParams['axes.unicode_minus'] = False
    return False


def load_data(input_file):
    """加载财务数据"""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    required_fields = ['company', 'revenue', 'profit']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必需字段: {field}")
    
    if len(data['revenue']) < 4:
        print(f"⚠️  警告: 数据点不足 ({len(data['revenue'])}个)，建议至少8个季度")
    
    return data


def calculate_growth_rates(values):
    """计算同比增长率"""
    growth_rates = []
    for i in range(len(values)):
        if i >= 4 and values[i-4] != 0:  # 同比需要对比4个季度前
            rate = ((values[i] - values[i-4]) / abs(values[i-4])) * 100
            growth_rates.append(rate)
        else:
            growth_rates.append(None)
    return growth_rates


def generate_static_chart(data, output_dir):
    """生成 PNG 静态图"""
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    
    company = data['company']
    periods = [item['period'] for item in data['revenue']]
    revenues = [item['value'] for item in data['revenue']]
    profits = [item['value'] for item in data['profit']]
    
    # 计算增长率
    revenue_growth = calculate_growth_rates(revenues)
    profit_growth = calculate_growth_rates(profits)
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle(f'{company} - 核心财务指标趋势', fontsize=16, fontweight='bold')
    
    # 上图：收入与利润
    x = range(len(periods))
    line1 = ax1.plot(x, revenues, 'o-', color='#FF6A00', linewidth=2, markersize=6, label='收入')
    line2 = ax1.plot(x, profits, 's-', color='#007AFF', linewidth=2, markersize=6, label='利润')
    
    # 添加数值标签
    for i, (rev, prof) in enumerate(zip(revenues, profits)):
        if i % 2 == 0:  # 每隔一个点标注，避免拥挤
            ax1.annotate(f'{rev:.0f}', (i, rev), textcoords="offset points", 
                        xytext=(0, 10), ha='center', fontsize=8, color='#FF6A00')
            ax1.annotate(f'{prof:.0f}', (i, prof), textcoords="offset points", 
                        xytext=(0, -15), ha='center', fontsize=8, color='#007AFF')
    
    ax1.set_xlabel('季度', fontsize=12)
    ax1.set_ylabel('金额 (亿元)', fontsize=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(periods, rotation=45, ha='right')
    ax1.legend(loc='upper left', fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.ticklabel_format(style='plain', axis='y')
    
    # 下图：同比增长率
    valid_rev_growth = [(i, g) for i, g in enumerate(revenue_growth) if g is not None]
    valid_prof_growth = [(i, g) for i, g in enumerate(profit_growth) if g is not None]
    
    if valid_rev_growth:
        idx_rev, vals_rev = zip(*valid_rev_growth)
        ax2.bar([i-0.2 for i in idx_rev], vals_rev, width=0.4, 
                color='#FF6A00', alpha=0.7, label='收入同比增速')
    
    if valid_prof_growth:
        idx_prof, vals_prof = zip(*valid_prof_growth)
        ax2.bar([i+0.2 for i in idx_prof], vals_prof, width=0.4, 
                color='#007AFF', alpha=0.7, label='利润同比增速')
    
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.set_xlabel('季度', fontsize=12)
    ax2.set_ylabel('同比增长率 (%)', fontsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(periods, rotation=45, ha='right')
    ax2.legend(loc='upper left', fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.tight_layout()
    
    # 保存图片
    output_file = os.path.join(output_dir, f'{company}_trends.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ 静态图已保存: {output_file}")
    return output_file


def generate_interactive_chart(data, output_dir):
    """生成 HTML 交互图"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    company = data['company']
    periods = [item['period'] for item in data['revenue']]
    revenues = [item['value'] for item in data['revenue']]
    profits = [item['value'] for item in data['profit']]
    
    # 创建子图
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=('收入与利润趋势', '同比增长率'),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # 上图：收入与利润
    fig.add_trace(
        go.Scatter(x=periods, y=revenues, name='收入',
                  line=dict(color='#FF6A00', width=3),
                  marker=dict(size=8, symbol='circle')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=periods, y=profits, name='利润',
                  line=dict(color='#007AFF', width=3),
                  marker=dict(size=8, symbol='square')),
        row=1, col=1
    )
    
    # 计算同比增长率
    revenue_growth = calculate_growth_rates(revenues)
    profit_growth = calculate_growth_rates(profits)
    
    # 下图：增长率
    fig.add_trace(
        go.Bar(x=periods, y=revenue_growth, name='收入同比增速',
              marker_color='#FF6A00', opacity=0.7),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(x=periods, y=profit_growth, name='利润同比增速',
              marker_color='#007AFF', opacity=0.7),
        row=2, col=1
    )
    
    # 更新布局
    fig.update_layout(
        title=f'{company} - 核心财务指标趋势分析',
        height=800,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(title_text="季度", row=2, col=1)
    fig.update_yaxes(title_text="金额 (亿元)", row=1, col=1)
    fig.update_yaxes(title_text="同比增长率 (%)", row=2, col=1)
    
    # 保存 HTML
    output_file = os.path.join(output_dir, f'{company}_trends.html')
    fig.write_html(output_file, include_plotlyjs='cdn', full_html=True)
    
    print(f"✅ 交互图已保存: {output_file}")
    return output_file


def main():
    if len(sys.argv) != 3:
        print("用法: python3 visualize_trends.py <input_json> <output_dir>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # 设置中文字体
        setup_chinese_font()
        
        # 加载数据
        print(f"📊 加载数据: {input_file}")
        data = load_data(input_file)
        print(f"🏢 公司: {data['company']}")
        print(f"📈 数据点数: {len(data['revenue'])} 个季度")
        
        # 生成静态图
        print("\n🎨 生成静态图...")
        png_path = generate_static_chart(data, output_dir)
        
        # 生成交互图
        print("\n🌐 生成交互图...")
        html_path = generate_interactive_chart(data, output_dir)
        
        # 输出结果 JSON
        result = {
            "static_chart": png_path,
            "interactive_chart": html_path,
            "company": data['company'],
            "data_points": len(data['revenue']),
            "generated_at": datetime.now().isoformat()
        }
        
        print("\n" + "="*50)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("="*50)
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
