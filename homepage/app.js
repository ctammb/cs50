const APP = {
    data: [],
    init() {
        APP.addListeners();
    },
    addListeners() {
        const form = document.querySelector('#collect form');

        form.addEventListener('submit', () => {
            if(document.getElementById("foodShort").checked) {
                document.getElementById('hiddenFoodShort').disabled = true;
            }
        });
        form.addEventListener('submit', () => {
            if(document.getElementById("foodLong").checked) {
                document.getElementById('hiddenFoodLong').disabled = true;
            }
        });
        form.addEventListener('submit', () => {
            if(document.getElementById("housing").checked) {
                document.getElementById('hiddenHousing').disabled = true;
            }
        });
        form.addEventListener('submit', () => {
            if(document.getElementById("flid").checked) {
                document.getElementById('hiddenFlid').disabled = true;
            }
        });
        form.addEventListener('submit', () => {
            if(document.getElementById("employment").checked) {
                document.getElementById('hiddenEmployment').disabled = true;
            }
        });
        form.addEventListener('submit', () => {
            if(document.getElementById("medical").checked) {
                document.getElementById('hiddenMedical').disabled = true;
            }
        });
        form.addEventListener('submit', () => {
            if(document.getElementById("legal").checked) {
                document.getElementById('hiddenLegal').disabled = true;
            }
        });
        form.addEventListener('submit', () => {
            if(document.getElementById("family").checked) {
                document.getElementById('hiddenFamily').disabled = true;
            }
        });
        form.addEventListener('submit', () => {
            if(document.getElementById("transportation").checked) {
                document.getElementById('hiddenTransportation').disabled = true;
            }
        });
        form.addEventListener('submit', () => {
            if(document.getElementById("bike").checked) {
                document.getElementById('hiddenBike').disabled = true;
            }
        });
        form.addEventListener('submit', () => {
            if(document.getElementById("computer").checked) {
                document.getElementById('hiddenComputer').disabled = true;
            }
        });
        form.addEventListener('submit', () => {
            if(document.getElementById("patio").checked) {
                document.getElementById('hiddenPatio').disabled = true;
            }
        });
        form.addEventListener('change', () => {
            if(document.getElementById("countyNo").checked === true) {
                document.getElementById('mtimeOp1').required = false;
            }
        });
        form.addEventListener('change', () => {
            if(document.getElementById("homelessNo").checked === true) {
                document.getElementById('htimeOp1').required = false;
            }
        });

        form.addEventListener('submit', APP.saveData);

        document
            .getElementById('btnExport')
            .addEventListener('click', APP.exportData);

        document
            .querySelector('table tbody')
            .addEventListener('dblclick', APP.editCell);
    },
    saveData(event) {
        event.preventDefault();
        const form = event.target;
        const formdata = new FormData(form);
        //save form in local storage
        const obj = Object.fromEntries(formdata);
        const json = JSON.stringify(obj);
        localStorage.setItem('form', json);
        //window.location.href = "plan.html";
        //save the data in APP.data
        APP.cacheData(formdata);
        //build a row in the table
        APP.buildRow(formdata);
        //clear the form
        form.reset();
        document.getElementById('hiddenFoodShort').disabled = false;
        document.getElementById('hiddenFoodLong').disabled = false;
        document.getElementById('hiddenHousing').disabled = false;
        document.getElementById('hiddenFlid').disabled = false;
        document.getElementById('hiddenEmployment').disabled = false;
        document.getElementById('hiddenMedical').disabled = false;
        document.getElementById('hiddenLegal').disabled = false;
        document.getElementById('hiddenFamily').disabled = false;
        document.getElementById('hiddenTransportation').disabled = false;
        document.getElementById('hiddenBike').disabled = false;
        document.getElementById('hiddenComputer').disabled = false;
        document.getElementById('hiddenPatio').disabled = false;
        //focus on first field
        document.getElementById('foodShort').focus();
    },
    cacheData(formdata) {
        //extract the data from the FormData object and update APP.data
        APP.data.push(Array.from(formdata.values()));
        console.table(APP.data);
    },
    buildRow(formdata) {
        const tbody = document.querySelector('#display > table > tbody');
        const tr = document.createElement('tr');
        tr.innerHTML = '';
        tr.setAttribute('data-row', document.querySelectorAll('tbody tr').length);
        let col=0;
        for(let entry of formdata.entries()){
            tr.innerHTML += `<td data-col="${col}" data-name="${entry[0]}">${entry[1]}</td>`;
            col++;
                }
        tbody.append(tr);
    },
    exportData() {
        //insert header row
        APP.data.unshift(['Food Short', 'Food Long', 'Housing', 'ID', 'Employment', 'Medical', 'Legal', 'Family', 'Transportation',
        'Bike', 'Computer', 'Patio', 'Hear', 'Resident',
        'Resident Time', 'Sleep', 'Homeless', 'Homeless Time', 'Special', 'Comments', 'CSIS']);
        //array to a string
        let str='';
        APP.data.forEach((row) => {
            str += row.map((col) => JSON.stringify(col)).join(',').concat('\n');
        });
        //create the file
        let filename = `intake.${Date.now()}.csv`;
        let file = new File([str], filename, {type: 'text/csv'});

        //create
        let a = document.createElement('a');
        a.href = URL.createObjectURL(file);
        a.download = filename;
        a.click();
        APP.data = [];
        $('#display > table > tbody > tr').remove();
    },
    editCell(ev) {
        let cell = ev.target.closest('td');
        let row = +cell.parentElement.getAttribute('data-row');
        let col = +cell.getAttribute('data-col');
        if (cell) {
          let row = +cell.parentElement.getAttribute('data-row');
          let col = +cell.getAttribute('data-col');
          //a td was clicked so make it editable
          cell.contentEditable = true;
          let txt = cell.textContent;
          cell.focus();
          cell.addEventListener('keydown', function save(ev) {
            //check for Enter key
            if (ev.key === 'Enter' || ev.code === 'Enter') {
              //disable contentEditable
              cell.contentEditable = false;
              //remove listener
              cell.removeEventListener('keydown', save);
              //update APP.data using the row value
              APP.data[row][col] = cell.textContent;
              //need to match the cell with the column based on row and col
              console.table(APP.data);
            }
          });
          //listen for the enter key to end the editing
          //update the APP.data
        }
      },
};

document.addEventListener('DOMContentLoaded', APP.init);
