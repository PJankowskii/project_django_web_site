const renderChartOne = (data, labels) => {
    const ctx = document.getElementById('myChartOne').getContext('2d');
    const myChartOne = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [
            {
                label: 'Last month expenses',
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            title:{
                display: true,
                text: "Last month expenses per category",
            },
        },
    });
};
const getChartDataOne=()=>{
    console.log('fetching')
    fetch('/expenses/summary-expense-category')
    .then((res) => res.json())
    .then((results) => {
        console.log('results', results);
        const category_data = results.expense_category_data_one;
        const [labels, data] = [Object.keys(category_data), Object.values(category_data)];
        renderChartOne(data, labels);
    });
};
document.onload=getChartDataOne();

const renderChartThree = (data, labels) => {
    const ctx = document.getElementById('myChartThree').getContext('2d');
    const myChartThree = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [
            {
                label: 'Last 3 months expenses',
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            title:{
                display: true,
                text: "Last 3 months expenses per category",
            },
        }
    });
};
const getChartDataThree=()=>{
    console.log('fetching')
    fetch('/expenses/summary-expense-category')
    .then((res) => res.json())
    .then((results) => {
        console.log('results', results);
        const category_data = results.expense_category_data_three;
        const [labels, data] = [Object.keys(category_data), Object.values(category_data)];
        renderChartThree(data, labels);
    });
};
document.onload=getChartDataThree();

const renderChart = (data, labels) => {
    const ctx = document.getElementById('myChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [
            {
                label: 'Last 6 months expenses',
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            title:{
                display: true,
                text: "Last 6 months expenses per category",
            },
        }
    });
};
const getChartData=()=>{
    console.log('fetching')
    fetch('/expenses/summary-expense-category')
    .then((res) => res.json())
    .then((results) => {
        console.log('results', results);
        const category_data = results.expense_category_data_six;
        const [labels, data] = [Object.keys(category_data), Object.values(category_data)];
        renderChart(data, labels);
    });
};
document.onload=getChartData();
