//firebase target:apply hosting site1 fir-hosting-test-78ed2


dict_of_usernames = {
    "jeremy.downey": 0,
    "varun_b_vibing": 0,
    "sarakargosha": 0,
    "j.zy.c": 0,
    "manpreet_bhatti": 0,
    "dimitri_tz": 0,
    "itsniqqi": 0,
    "stef.virgilio": 0,
    "riftasnia": 0,
    "deepsinghkalsi": 0,
    "erensolak45": 0,
    "laptopdestroyer": 0,
    "a_funnie_man": 0,
    "01h.art": 0,
    "jsphhlee": 0,
    "liamshanny": 0,
    "williamlutes": 0,
    "lyne_537": 0,
    "jack.pktz": 0,
    "noor.chxdhry": 0,
    "vai9er": 0,
    "thekamileon97": 0,
    "mdcosta3231": 0,
    "xi.h_": 0,
    "anushna_": 0,
    "brittrolston": 0,
    "alinxs7": 0,
    "areeba.z": 0,
    "zunair74": 0,
    "n.e.o.roaism": 0,
};



var database = firebase.database();

const activityTable = document.querySelector('#activity-table-body');
//const preObject = document.getElementById('object');

//create references

var dbRefObject = database.ref("groupchatDatabase/Members");
lastSortedColumn = 2;
// Reference the object when a value changes. Then provide the snapshot
dbRefObject.on('value', (snapshot) => {
    removeAllChildNodes(activityTable);
    memberList = snapshot.val();
    arrayOfMembers = turnObjectIntoArray(memberList);
    sortedArray = sortMemberListArray(arrayOfMembers, "Appearances");
    
    for (let index = (sortedArray.length-1);  index >= 0; index--){
        
        member = sortedArray[index];
        renderMembers(memberList, member, index);
    }
    
    sortTableByColumn(activityTable.parentElement, lastSortedColumn);
});

function turnObjectIntoArray(object){
    
    let objectArray = [];
    
    for (let subObject in object){
        objectArray.push(object[subObject]);
    }
    
    return objectArray;
    
}

function sortMemberListArray(array, arrayField){
    
    array.sort(function(a, b){return a[arrayField] - b[arrayField]});
    return array;
}
/* function countMessagesPerUsername(messages){


    for (let subObject in messages){
        if (messages[subObject]["Username"] in dict_of_usernames){
            dict_of_usernames[messages[subObject]["Username"]] = 0;
        }
    }
    
    for (let subObject in messages){
        if (messages[subObject]["Username"] in dict_of_usernames){
            dict_of_usernames[messages[subObject]["Username"]]++;
        }
    }
    
    
} */



function renderMembers(memberList, member, rank){
    let tr = document.createElement('tr');
    let username = document.createElement('td');
    let ranker = document.createElement('td');
    let comments = document.createElement('td');
    
    usernameOfMember = member["Username"].replace(/,/g, ".");    //The Firebase Realtime Database cannot have names with '.' in them.
    tr.setAttribute('data-id', usernameOfMember);
    username.textContent = usernameOfMember;
    ranker.textContent = 46-rank;
    comments.textContent = member["Message_Count"];
    
    tr.appendChild(ranker);
    tr.appendChild(username);
    tr.appendChild(comments);
    
    activityTable.appendChild(tr);

}

function removeAllChildNodes(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}


function sortTableByColumn(table, column, asc = true) {
    console.log("Check");
    const dirModifier = asc ? 1 : -1;
    const tBody = table.tBodies[0];
    const rows = Array.from(tBody.querySelectorAll("tr"));
    lastSortedColumn = column;
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
            
       var aColText = a.querySelector(`td:nth-child(${ 2 })`).textContent.trim();
       var bColText = b.querySelector(`td:nth-child(${ 2 })`).textContent.trim();
       
       return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
    });
    console.log(sortedRows); 
    
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

sortTableByColumn(document.querySelector("table"), 2, true);
 
document.querySelectorAll(".table-sortable .header-sortable").forEach(headerCell => {
    
    headerCell.addEventListener("click", () => {
        let tableElement = headerCell.closest("table");
        let headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
        
        let currentIsAscending = headerCell.classList.contains("th-sort-asc");
        
        sortTableByColumn(tableElement, headerIndex, !currentIsAscending);
    });

}); 