/* Chart Theme Configuration
   This JavaScript can be added to index.html to style all charts consistently 
   with the dark themed glassmorphic design */

// Chart.js 全局配置，使圖表風格與網站設計一致
function initChartTheme() {
    Chart.defaults.color = 'rgba(255, 255, 255, 0.7)';
    Chart.defaults.font.family = "'Noto Sans TC', sans-serif";
    
    const chartColors = {
        primary: '#60a5fa',
        secondary: '#818cf8',
        success: '#10b981',
        danger: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6',
        dark: 'rgba(255, 255, 255, 0.2)',
        backgroundOpacity: 0.2,
        borderOpacity: 0.8
    };
    
    // 生成具有透明度的顏色陣列
    const generateColors = (baseColor, count, opacity) => {
        const colors = [];
        const step = 1 / count;
        
        for (let i = 0; i < count; i++) {
            // 計算顏色的 HSL 值變化
            const hue = (i * step * 30) % 360; // 調整色相
            colors.push(`hsla(${hue}, 85%, 65%, ${opacity})`);
        }
        
        return colors;
    };
    
    // 為所有圖表設置統一的樣式
    const applyChartStyles = (chart) => {
        if (chart.config.type === 'line') {
            styleLineChart(chart);
        } else if (chart.config.type === 'bar') {
            styleBarChart(chart);
        } else if (chart.config.type === 'pie' || chart.config.type === 'doughnut') {
            stylePieChart(chart);
        }
    };
    
    // 折線圖樣式
    const styleLineChart = (chart) => {
        const datasets = chart.data.datasets;
        datasets.forEach((dataset, i) => {
            // 使用主色調和半透明
            dataset.borderColor = chartColors.primary;
            dataset.backgroundColor = `rgba(96, 165, 250, ${chartColors.backgroundOpacity})`;
            
            // 給線條添加漸變和圓角
            dataset.fill = true;
            dataset.tension = 0.4; // 使曲線更圓滑
            dataset.pointBackgroundColor = '#60a5fa';
            dataset.pointBorderColor = 'rgba(0, 0, 0, 0.2)';
            dataset.pointHoverRadius = 6;
            dataset.pointHoverBackgroundColor = '#ffffff';
            dataset.pointHoverBorderColor = chartColors.primary;
        });
    };
    
    // 柱狀圖樣式
    const styleBarChart = (chart) => {
        const datasets = chart.data.datasets;
        const dataLength = datasets[0]?.data?.length || 0;
        
        datasets.forEach((dataset, i) => {
            // 為每個柱子生成漸變的顏色
            if (datasets.length === 1 && dataLength > 1) {
                dataset.backgroundColor = generateColors(chartColors.primary, dataLength, chartColors.backgroundOpacity);
                dataset.borderColor = generateColors(chartColors.primary, dataLength, chartColors.borderOpacity);
            } else {
                const baseColor = Object.values(chartColors)[i % 6];
                dataset.backgroundColor = `${baseColor}${(chartColors.backgroundOpacity * 255 | 0).toString(16).padStart(2, '0')}`;
                dataset.borderColor = baseColor;
            }
            
            dataset.borderWidth = 1;
            dataset.borderRadius = 6;
            dataset.hoverBackgroundColor = dataset.backgroundColor.replace(
                chartColors.backgroundOpacity, 
                chartColors.backgroundOpacity + 0.1
            );
            dataset.hoverBorderColor = dataset.borderColor;
        });
    };
    
    // 圓餅圖樣式
    const stylePieChart = (chart) => {
        const datasets = chart.data.datasets;
        const dataLength = datasets[0]?.data?.length || 0;
        
        datasets.forEach(dataset => {
            dataset.backgroundColor = generateColors(chartColors.primary, dataLength, chartColors.backgroundOpacity + 0.3);
            dataset.borderColor = 'rgba(255, 255, 255, 0.1)';
            dataset.borderWidth = 2;
            dataset.hoverOffset = 10;
            dataset.hoverBackgroundColor = generateColors(chartColors.primary, dataLength, chartColors.backgroundOpacity + 0.5);
        });
    };
    
    // 設置圖表格線和刻度的樣式
    Chart.defaults.scales.linear.grid.color = 'rgba(255, 255, 255, 0.05)';
    Chart.defaults.scales.linear.grid.drawBorder = false;
    Chart.defaults.scales.linear.ticks.padding = 10;
    
    Chart.defaults.scales.category.grid.color = 'rgba(255, 255, 255, 0.05)';
    Chart.defaults.scales.category.grid.drawBorder = false;
    Chart.defaults.scales.category.ticks.padding = 10;
    
    // 註冊插件來應用全局樣式
    const glassmorphicPlugin = {
        id: 'glassmorphicPlugin',
        beforeInit: (chart) => {
            applyChartStyles(chart);
        }
    };
    
    Chart.register(glassmorphicPlugin);
}

// 在頁面載入時初始化圖表主題
document.addEventListener('DOMContentLoaded', initChartTheme);
