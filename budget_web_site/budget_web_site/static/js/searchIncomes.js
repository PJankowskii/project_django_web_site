const searchField = document.querySelector("#searchField");

const tableOutput = document.querySelector(".table-output");
const tableApp = document.querySelector(".table-app");

const paginationContainer = document.querySelector(".pagination-container");

const tableBody = document.querySelector(".table-body");

const noResults = document.querySelector(".no-results");

tableOutput.style.display = "none";
noResults.style.display = "none";

searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;

    if(searchValue.trim().length > 0) {
        tableBody.innerHTML = "";
        paginationContainer.style.display = "none";
        console.log('searchValue', searchValue);

        fetch("/incomes/search-incomes", {
            body: JSON.stringify({ searchText: searchValue }),
            method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
                console.log("data", data);

                tableApp.style.display = "none";
                tableOutput.style.display = "block";

                if(data.length===0){
                    noResults.style.display = "block";
                    tableOutput.style.display="none";
                } else {
                    noResults.style.display = "none";
                    data.forEach(item => {
                    const link_edit = '<a class=text-info href=/incomes/edit-income/' + item.id + '>Edit</a>';
                    tableBody.innerHTML += `
                    <tr>
                        <td>${item.amount}</td>
                        <td>${item.source}</td>
                        <td>${item.description}</td>
                        <td>${item.date}</td>
                        <td>${link_edit}</td>
                    </tr>`;
                    });
                }
        });
    } else {
        tableOutput.style.display="none";
        tableApp.style.display = "block";
        paginationContainer.style.display = "block";
    }
});