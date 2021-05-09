//firebase target:apply hosting site1 fir-hosting-test-78ed2
// Note: I get warnings from JSDoc for putting @type and descriptions on the same line, but it works fine
/** 
 * Database parent node. Each group chat has its own parent node, so each site references a different node.
 * databaseName should be the only different value across sites.
 * @type {string}
 */
const databaseName = 'groupchatDatabase';
const database = firebase.database();
const activityTable = document.querySelector('#activity-table-body');

/** @type {database.ref} - The database reference to where count of each member's messages is stored */
const dbRefObject = database.ref(databaseName + '/Members');
/** @type {integer} - The column that the activity table is sorted by. Default is column 2 (# of messages). */
let lastSortedColumn = 2;
let chartExists = false;
/* @type {Chart} - The bar/doughnut graph container. Initialized outside the scope of the db listener so it can be altered.*/
let activityGraph;
/* @type {Object} - The data fed into the graph. Initialized outside the scope of the db listener so it can be altered.*/
let data;
/* @type {Object} - The raw data to be filtered into the graph. Initialized outside the scope of the db listener so it doesn't change as past the site loading.*/
let arrayOfMembersStored;
// Create the activity table and the myChart 
dbRefObject.on('value', (snapshot) => {
  removeAllChildNodes(/* parent= */ activityTable);
  const memberList = snapshot.val();
  const arrayOfMembers = turnObjectIntoArray(/* object= */ memberList);
  const sortedArray = sortArray(/* array= */ arrayOfMembers, /* arrayField= */ "Message_Count");
  
  renderMembers(sortedArray);
  
  sortTableByColumn(/* table= */ activityTable.parentElement, /*column= */ lastSortedColumn);
  
  data = createData(/* rawData= */ arrayOfMembers);
  if (!chartExists) {
    arrayOfMembersStored = arrayOfMembers;
    activityGraph = new Chart(myChart, data);
    chartExists = true; 
  }
});

/**
  * Takes an object, and pushes each value within that object into an array.
  * Arrays are just easier to sort.
  * @param {object} object An object that will be turned into an array.
  * @returns {array} returnArray An array made of the values of the object.
  */
function turnObjectIntoArray(object) {
  const returnArray = [];
  for (let property in object) {
    returnArray.push(object[property]);
  }
  return returnArray;
}

/**
  * Sorts an array of objects by a field.
  * @param {array.<object>} array An array of objects to be sorted.
  * @param {string} arrayField The key to the field the array will be sorted by.
  * @returns {array} array The finished sorted array.
  */
function sortArray(array, arrayField) {
  
  array.sort(function(a, b) {return a[arrayField] - b[arrayField]});
  return array;
}

/**
  * Puts the activity data into the activity data so it is actually visible.
  * @param {array.<object>} memberArray An array of members to be put in the table.
  * @returns {void} 
  */
function renderMembers(memberArray) {
  for (const [index, member] of memberArray.entries()){
    const tr = document.createElement('tr');
    const username = document.createElement('td');
    const ranker = document.createElement('td');
    const comments = document.createElement('td');
    
    usernameOfMember = member['Username'].replace(/,/g, '.');  //The Firebase Realtime Database cannot have names with '.' in them.
    tr.setAttribute('data-id', usernameOfMember);
    username.textContent = usernameOfMember;
    ranker.textContent = 46-index;
    comments.textContent = member['Message_Count'];
    
    tr.appendChild(ranker);
    tr.appendChild(username);
    tr.appendChild(comments);
    activityTable.appendChild(tr);
  }
}  

/**
  * Removes the child nodes from an HTML element.
  * @param {Element} parent A parent HTML element.
  * @returns {void} 
  */  
function removeAllChildNodes(parent) {
  while (parent.firstChild) {
    parent.removeChild(parent.firstChild);
  }
}

/**
  * Sorts an HTML table by a given column.
  * @param {Element} parent A parent HTML element.
  * @param {integer} column The number, starting from left at 0, of the column to sort by in the table.
  * @param {boolean} asc Whether to sort from high to low or from low to high.
  * @returns {void} 
  */
function sortTableByColumn(table, column, asc = true) {
  const dirModifier = asc ? 1 : -1;
  const tBody = table.tBodies[0];
  const rows = Array.from(tBody.querySelectorAll('tr'));
  lastSortedColumn = column;
  // Sort each row
  const sortedRows = rows.sort((a, b) => {
    var aColText = a.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();
    var bColText = b.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();

    if (!isNaN(aColText)) {
       aColText = -1*parseInt(aColText);
       bColText = -1*parseInt(bColText);
    } 
    if (aColText != bColText) {
      return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
    }
      
     var aColText = a.querySelector(`td:nth-child(${ 2 })`).textContent.trim();
     var bColText = b.querySelector(`td:nth-child(${ 2 })`).textContent.trim();
     
     return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
  });
  //Remove all existing TRs from the table
  while (tBody.firstChild) {
    tBody.removeChild(tBody.firstChild);
  }
  // Re-add the newly sorted rows
  for (let index = 0;  index < sortedRows.length; index++) {
    sortedRows[index].firstChild.textContent = index+1;
    tBody.append(sortedRows[index]);
  }
  // Remember how the column is currently sorted
  table.querySelectorAll("th").forEach(th => th.classList.remove('th-sort-asc', 'th-sort-desc'));
  table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle('th-sort-asc', asc);
  table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle('th-sort-desc', !asc);
}

// Adds in the on click function to the headers of the table that lets the table be sorted by that column by clicking on the header. 
document.querySelectorAll(".table-sortable .header-sortable").forEach(headerCell => {
  headerCell.addEventListener("click", () => {
    const tableElement = headerCell.closest("table");
    const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);   
    const currentIsAscending = headerCell.classList.contains("th-sort-asc");
    sortTableByColumn(/* table= */ tableElement, /*column= */ headerIndex, /* ascending= */ !currentIsAscending);
  });
}); 

/*  MY CHART CODE    */

const myChart = document.getElementById('my-chart').getContext('2d');
//Global Options
Chart.defaults.global.defaultFontFamily ='Lato';
Chart.defaults.global.defaultFontSize = 18;
Chart.defaults.global.defaultFontColor = '#777';

/**
  * Creates the formatted data and settings that's input to create the myChart.
  * @param {array.<object>} rawData The array of objects containing data to create the chart.
  * @returns {object} formattedData The data object formatted in the way myChart wants.
  */
function createData (rawData) {
  
  num_of_comments_list = [];
  names_list = [];
  colour_list = [];
  sumOfMessages = 0;
  rawData.forEach(item => {
    sumOfMessages += item['Message_Count'];
  });
  
  numUsers = document.querySelector('.users-displayed-input').value;
  console.log('numUsers:');
  console.log(numUsers);
  rawDataFiltered = rawData.filter((datum , index) => (30-numUsers < index)); 
  
  rawDataFiltered.forEach((item, index) => {
    console.log(item);
    names_list.push(item['Username'].replace(/,/g, "."));
    num_of_comments_list.push(item['Message_Count']);
    hue = index * (360/rawDataFiltered.length);
    colour_list.push(`hsla(${hue}, 70%, 70%, 0.8`);
  });
  
  formattedData = {
    type: 'bar', //bar, horizontalBar, pie, line, doughnut, radar, polarArea
    data: {
      labels: names_list,
      datasets:[{
        label:'Number of Messages',
        data: num_of_comments_list,
        //backgroundColor:'green'
        backgroundColor: colour_list,
        borderWidth: 1,
        borderColor:'#777',
        hoverBorderWidth: 3,
        hoverBorderColor: '#FFF',
      }],
    },
    options: {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }]
      }
    },
  }
  return formattedData;
}

chartButton = document.querySelector('.chart-type-button');

chartButton.addEventListener('click', () =>{
  console.log(activityGraph);
  tempData = activityGraph.data;
  tempOptions = activityGraph.options;
  tempType = activityGraph.config.type;
  activityGraph.destroy();
  if (activityGraph.config.type === 'bar') {    
    activityGraph = new Chart(myChart, {
      type: 'doughnut',
      data: tempData,
    });
    chartButton.value = 'Bar chart';
  }else {
     activityGraph = new Chart(myChart, {
      type: 'bar',
      data: tempData,
      options: {
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: true
            }
          }]
        }
      }
    });
    chartButton.value = 'Doughnut chart';
  }
});

document.querySelector('.users-displayed-input').addEventListener('change', (event) => {
  console.log('Check2 for arrayOfMembers');
  const tempData = createData(arrayOfMembersStored);
  const tempOptions = activityGraph.options;
  const tempType = activityGraph.config.type;
  activityGraph.destroy();
  activityGraph = new Chart(myChart, {
    type: tempType,
    data: tempData.data,
    options: tempOptions,
  });
});