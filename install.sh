#!/bin/bash
# 财报三维度分析 Skill v2.0 - 安装脚本

set -e

echo "🚀 开始安装财报三维度分析 Skill v2.0..."
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📂 安装源目录：${SCRIPT_DIR}"
echo ""

# 步骤 1：检查 Python 环境
echo "🐍 步骤 1: 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 Python3${NC}"
    echo "请先安装 Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python 版本：${PYTHON_VERSION}"
echo ""

# 步骤 2：安装 Python 依赖
echo "📦 步骤 2: 安装 Python 依赖..."
echo "正在安装 matplotlib 和 plotly..."

pip3 install matplotlib plotly -q

if python3 -c "import matplotlib" && python3 -c "import plotly"; then
    echo -e "${GREEN}✅ 依赖安装成功${NC}"
else
    echo -e "${RED}❌ 依赖安装失败${NC}"
    exit 1
fi
echo ""

# 步骤 3：验证可视化脚本
echo "🧪 步骤 3: 验证可视化脚本..."

# 创建测试数据
TEST_DATA='{"company":"测试公司","revenue":[{"period":"2023Q1","value":100},{"period":"2023Q2","value":110},{"period":"2023Q3","value":120},{"period":"2023Q4","value":130},{"period":"2024Q1","value":140},{"period":"2024Q2","value":150},{"period":"2024Q3","value":160},{"period":"2024Q4","value":170},{"period":"2025Q1","value":180},{"period":"2025Q2","value":190},{"period":"2025Q3","value":200},{"period":"2025Q4","value":210}],"profit":[{"period":"2023Q1","value":20},{"period":"2023Q2","value":25},{"period":"2023Q3","value":30},{"period":"2023Q4","value":35},{"period":"2024Q1","value":40},{"period":"2024Q2","value":45},{"period":"2024Q3","value":50},{"period":"2024Q4","value":55},{"period":"2025Q1","value":60},{"period":"2025Q2","value":65},{"period":"2025Q3","value":70},{"period":"2025Q4","value":75}]}'

TEST_FILE="/tmp/test_financial_v2.json"
echo "$TEST_DATA" > "$TEST_FILE"

OUTPUT_DIR="/tmp/test_viz_v2_output"
mkdir -p "$OUTPUT_DIR"

if python3 "${SCRIPT_DIR}/scripts/visualize_trends.py" "$TEST_FILE" "$OUTPUT_DIR" > /tmp/viz_v2_test.log 2>&1; then
    echo -e "${GREEN}✅ 可视化脚本测试通过${NC}"
    
    # 显示生成的文件
    echo ""
    echo "📈 测试生成的图表："
    ls -lh "$OUTPUT_DIR"/*.png 2>/dev/null | awk '{print "   - " $NF " (" $5 ")"}' || true
    ls -lh "$OUTPUT_DIR"/*.html 2>/dev/null | awk '{print "   - " $NF " (" $5 ")"}' || true
else
    echo -e "${YELLOW}⚠️  可视化脚本测试失败，但不影响安装${NC}"
    echo "查看日志：/tmp/viz_v2_test.log"
fi

# 清理测试文件
rm -rf "$OUTPUT_DIR" "$TEST_FILE"
echo ""

# 步骤 4：提供安装指引
echo "=========================================="
echo -e "${GREEN}🎉 预安装检查完成！${NC}"
echo ""
echo "📋 下一步操作："
echo ""
echo "方法 1：通过 real_cli 安装（推荐）"
echo "   real_cli skills install local --json '{\"sourcePath\": \"${SCRIPT_DIR}\"}'"
echo ""
echo "方法 2：手动复制文件到 skill 目录"
echo "   1. 找到已安装的 skill 目录 (~/.skills/f1633e17-...)"
echo "   2. 备份原有文件"
echo "   3. 复制 scripts/visualize_trends.py 到 scripts/"
echo "   4. 替换 SKILL.md"
echo ""
echo "=========================================="
echo ""
echo "✅ 安装准备就绪！"
