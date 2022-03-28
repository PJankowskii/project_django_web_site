const renderChartOne = (data, labels) => {
    const ctx = document.getElementById('myChartOne').getContext('2d');
    const myChartOne = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
            {
                label: 'Last month expenses per category',
                data: data,
                borderColor: 'rgb(0, 0, 0)',
                borderWidth: 1
            }]
        },
    });
};
const getChartDataOne=()=>{
    console.log('fetching')
    fetch('/summary-last-month-expenses')
    .then((res) => res.json())
    .then((results) => {
        console.log('results', results);
        const category_data = results.expense_category_data;
        const [labels, data] = [Object.keys(category_data), Object.values(category_data)];
        renderChartOne(data, labels);
    });
};
document.onload=getChartDataOne();

const renderChartTwo = (data, labels) => {
    const ctx = document.getElementById('myChartTwo').getContext('2d');
    const myChartTwo = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
            {
                label: 'Last month incomes per source',
                data: data,
                borderColor: 'rgb(0, 0, 0)',
                borderWidth: 1
            }]
        },
    });
};
const getChartDataTwo=()=>{
    console.log('fetching')
    fetch('/summary-last-month-incomes')
    .then((res) => res.json())
    .then((results) => {
        console.log('results', results);
        const category_data = results.income_source_data;
        const [labels, data] = [Object.keys(category_data), Object.values(category_data)];
        renderChartTwo(data, labels);
    });
};
document.onload=getChartDataTwo();