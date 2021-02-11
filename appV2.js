var database = firebase.database();

const activityTable = document.querySelector('#activity-table-body');
//const preObject = document.getElementById('object');

//create references

var dbRefObject = database.ref('Members');
lastSortedColumn = 2;
// Reference the object when a value changes. Then provide the snapshot
dbRefObject.orderByChild("Appearances").on('value', (snapshot) => {
    console.log("Change made");
    removeAllChildNodes(activityTable);
    //addHeaderToTable();
    memberList = snapshot.val();
    console.log(memberList);
    arrayOfMembers = turnObjectIntoArray(memberList);
    sortedArray = sortMemberListArray(arrayOfMembers, "Appearances");
    
    for (let index = (sortedArray.length-1);  index > 0; index--){
        
        member = sortedArray[index];
        renderMembers(memberList, member, index);
    }
    
    sortTableByColumn(activityTable.parentElement, lastSortedColumn);
});

// Listen for when there is an update to the database
// Clear table
// Call renderActivity on every item in database

// create element & render cafe
function renderMembers(memberList, member, rank){
    console.log("Render Members");
    let tr = document.createElement('tr');
    let username = document.createElement('td');
    let appearances = document.createElement('td');
    let likes = document.createElement('td');
    let ranker = document.createElement('td');
    let pokemon = document.createElement('td');
    let numOfPokemon = document.createElement('td');
    
    //console.log("Unaltered username: ");
    //console.log(member["Username"]);
    usernameOfMember = member["Username"].replace(/,/g, ".");    //The Firebase Realtime Database cannot have names with '.' in them.
    //console.log("Altered username: ");
    //console.log(usernameOfMember);
    tr.setAttribute('data-id', usernameOfMember);
    username.textContent = usernameOfMember;
    appearances.textContent = member["Appearances"];
    likes.textContent = member["Likes"];
    ranker.textContent = 46-rank;
    pokemon.textContent = member["Pokemon"]
    numOfPokemon.textContent = (member["Pokemon"].split(" ").length-1);
    
    tr.appendChild(ranker);
    tr.appendChild(username);
    tr.appendChild(appearances);
    tr.appendChild(likes);
    tr.appendChild(pokemon);
    tr.appendChild(numOfPokemon);
    
    activityTable.appendChild(tr);

}


function removeAllChildNodes(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}

function addHeaderToTable(){
    
    let tr = document.createElement('tr');
    let username = document.createElement('th');
    let appearances = document.createElement('th');
    let likes = document.createElement('th');
    let ranker = document.createElement('th');
    let pokemon = document.createElement('th');
    let numOfPokemon = document.createElement('th');
    
    
    username.textContent = "Username";
    appearances.textContent = "Appearances";
    likes.textContent = "4+ Likes Received";
    ranker.textContent = "Rank";
    pokemon.textContent = "Pokemon"
    numOfPokemon.textContent = "Number of Pokemon";
    
    tr.appendChild(ranker);
    tr.appendChild(username);
    tr.appendChild(appearances);
    tr.appendChild(likes);
    tr.appendChild(pokemon);
    tr.appendChild(numOfPokemon);
    
    activityTable.appendChild(tr);
    
}

function turnObjectIntoArray(object){
    
    let objectArray = [];
    
    for (let subObject in object){
        objectArray.push(object[subObject]);
    }
    
    return objectArray;
    
}

function sortMemberListArray(array, arrayField){
    
    console.log("Sort Member List Array");
    array.sort(function(a, b){return a[arrayField] - b[arrayField]});
    return array;
}

// real-time listener
/* db.collection('Groupchat_Activity').orderBy('Appearances', "desc").onSnapshot(snapshot => {
    let changes = snapshot.docChanges();
    counter = 0;
    changes.forEach(change => {
        counter++;
        console.log(change.doc.data());
        if(change.type == 'added'){
            renderActivity(change.doc, counter);
        } 
    });
});  */


/* Sorting Table */

function sortTableByColumn(table, column, asc = true) {
    console.log("Check");
    const dirModifier = asc ? 1 : -1;
    const tBody = table.tBodies[0];
    const rows = Array.from(tBody.querySelectorAll("tr"));
    lastSortedColumn = column;
    //var rows = [];
    
    /* for (i = 0; i < tempRows.length; i++){
        rows.push(tempRows[i]);
    } */
    //console.log(tempRows);
    //console.log(rows);
    // Sort each row
    const sortedRows = rows.sort((a, b) => {
        var aColText = a.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();
        var bColText = b.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();

        console.log(aColText);
        console.log(bColText);
        console.log(aColText > bColText);
        if (!isNaN(aColText)){
           aColText = -1*parseInt(aColText);
           bColText = -1*parseInt(bColText);
        } 
        if (aColText != bColText) {
            return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
        }
            
       //console.log("Selected column has equal value, default to sort by name");
       //console.log(aColText);
       var aColText = a.querySelector(`td:nth-child(${ 2 })`).textContent.trim();
       var bColText = b.querySelector(`td:nth-child(${ 2 })`).textContent.trim();
       
       return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
    });
    console.log(sortedRows); 
    
    //sortedRows = sortRows(rows, column, asc);
    console.log(sortedRows);
    //Remove all existing TRs from the table
    while (tBody.firstChild){
        tBody.removeChild(tBody.firstChild);
    }
    
    // Re-add the newly sorted rows
    
    
    for (let index = 0;  index < sortedRows.length; index++){
        sortedRows[index].firstChild.textContent = index+1;
        tBody.append(sortedRows[index]);
    }
    
    // Remember how the column is currently sorted
    
    table.querySelectorAll("th").forEach(th => th.classList.remove("th-sort-asc", "th-sort-desc"));
    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-asc", asc);
    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-desc", !asc);
}

function sortRows(rows, column, dir, asc){
    //console.log("Dir: " + dir);
    let n = rows.length;
        for (let i = 1; i < n; i++) {
            // Choosing the first element in our unsorted subarray
            let current = rows[i];
            // The last element of our sorted subarray
            let j = i-1; 
            if (asc){
                while ((j > -1) && (current.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim() < rows[j].querySelector(`td:nth-child(${ column + 1 })`).textContent.trim())) {
                    rows[j+1] = rows[j];
                    j--;
                }
            }else{
               while ((j > -1) && (current.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim() > rows[j].querySelector(`td:nth-child(${ column + 1 })`).textContent.trim())) {
                    rows[j+1] = rows[j];
                    j--;
                } 
            }
            rows[j+1] = current;
        }
    return rows;
}

/* tableHeaderElementNodeList = document.querySelectorAll(".table-sortable th");

for (let index = 1;  index < tableHeaderElementNodeList.length; index++){
    
    headerCell = tableHeaderElementNodeList.item(index);
    console.log(headerCell);
    headerCell.addEventListener("click", () => {
        var tableElement = headerCell.closest("table");
        var headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
        
        var currentIsAscending = headerCell.classList.contains("th-sort-asc");
        
        sortTableByColumn(tableElement, headerIndex, !currentIsAscending);
    });
    
} */

sortTableByColumn(document.querySelector("table"), 2, true);
 
document.querySelectorAll(".table-sortable .header-sortable").forEach(headerCell => {
    
    headerCell.addEventListener("click", () => {
        let tableElement = headerCell.closest("table");
        let headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
        
        let currentIsAscending = headerCell.classList.contains("th-sort-asc");
        
        sortTableByColumn(tableElement, headerIndex, !currentIsAscending);
    });

}); 