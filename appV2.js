const database = firebase.database();

const activityTable = document.querySelector('#activity-table');
//const preObject = document.getElementById('object');

//create references

const dbRefObject = database.ref('Members');

// Reference the object when a value changes. Then provide the snapshot
dbRefObject.orderByChild("Appearances").on('value', snap => {

    memberList = snap.val();
    arrayOfMembers = turnObjectIntoArray(memberList);
    sortedArray = sortMemberListArray(arrayOfMembers);
    
    for (let index = (sortedArray.length-1);  index > 0; index--){
        
        member = sortedArray[index];
        renderMembers(memberList, member, index)
    }
    
    
});

// Listen for when there is an update to the database
// Clear table
// Call renderActivity on every item in database

// create element & render cafe
function renderMembers(memberList, member, rank){
    let tr = document.createElement('tr');
    let username = document.createElement('td');
    let appearances = document.createElement('td');
    let likes = document.createElement('td');
    let ranker = document.createElement('td');
    
    
    console.log("Unaltered username: ");
    console.log(member["Username"]);
    usernameOfMember = member["Username"].replace(/,/g, ".");    //The Firebase Realtime Database cannot have names with '.' in them.
    console.log("Altered username: ");
    console.log(usernameOfMember);
    tr.setAttribute('data-id', usernameOfMember);
    username.textContent = usernameOfMember;
    appearances.textContent = member["Appearances"];
    likes.textContent = member["Likes"];
    ranker.textContent = 46-rank;
    
    tr.appendChild(ranker);
    tr.appendChild(username);
    tr.appendChild(appearances);
    tr.appendChild(likes);
    
    activityTable.appendChild(tr);

}


// create element & render cafe
function renderActivity(doc, rank){
    let tr = document.createElement('tr');
    let username = document.createElement('td');
    let appearances = document.createElement('td');
    let likes = document.createElement('td');
    let ranker = document.createElement('td');
    
    tr.setAttribute('data-id', doc.id);
    username.textContent = doc.data().Username;
    appearances.textContent = doc.data().Appearances;
    likes.textContent = doc.data().Likes
    ranker.textContent = rank
    
    tr.appendChild(ranker);
    tr.appendChild(username);
    tr.appendChild(appearances);
    tr.appendChild(likes);
    
    activityTable.appendChild(tr);

}

function turnObjectIntoArray(object){
    
    let objectArray = []
    
    for (let subObject in object){
        objectArray.push(object[subObject]);
    }
    
    return objectArray;
    
}

function sortMemberListArray(array){
    
    
    array.sort(function(a, b){return a["Appearances"] - b["Appearances"]});
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