var database = firebase.database();

const activityTable = document.querySelector('#activity-table-body');
//const preObject = document.getElementById('object');

//create references

namesRefObject = database.ref("groupchatDatabase/Members");
let arrayOfMembers = [];
let membersTimestamps = {};
namesRefObject.once('value', (snapshot) => {
    let memberList = snapshot.val();
    arrayOfMembers = turnObjectIntoArray(memberList);
    
    for (let index = 0;  index < arrayOfMembers.length; index++){
        arrayOfMembers[index]["Checked"] = false;
        membersTimestamps[arrayOfMembers[index]["Username"].replace(/,/g, ".")] = [];
    }
    
    removeAllChildNodes(checkbox_container1);
    removeAllChildNodes(checkbox_container2);
    removeAllChildNodes(checkbox_container3);
    put_members_in_divs(arrayOfMembers, "Message_Count");
    sortAlphaOrComments.value = "Sort Alphabetically";
});

checkbox_container1 = document.querySelector('#con1');
checkbox_container2 = document.querySelector('#con2');
checkbox_container3 = document.querySelector('#con3');

function put_members_in_divs(arrayOfMembers, field){
    
    let sortedArray = sortMemberListArray(arrayOfMembers, field);
    
    for (let index = 0;  index < sortedArray.length; index++){
        
        member = sortedArray[index];
        render_checkboxes(member, index % 3);
    }
    
}

sortAlphaOrComments = document.querySelector(".sortAlphaOrComments");
sortAlphaOrComments.addEventListener("click", () =>{
    
    if (sortAlphaOrComments.value == "Sort Alphabetically"){
        removeAllChildNodes(checkbox_container1);
        removeAllChildNodes(checkbox_container2);
        removeAllChildNodes(checkbox_container3);
        put_members_in_divs(arrayOfMembers, "Username");
        sortAlphaOrComments.value = "Sort by Message Count";
    }else{
        removeAllChildNodes(checkbox_container1);
        removeAllChildNodes(checkbox_container2);
        removeAllChildNodes(checkbox_container3);
        put_members_in_divs(arrayOfMembers, "Message_Count");
        sortAlphaOrComments.value = "Sort Alphabetically";
    }
    
});

function render_data_points(member){
    for (let index = 0;  index < arrayOfMembers.length; index++){
            
        if (arrayOfMembers[index]["Username"] == member["Username"]){
            console.log("Check");
            arrayOfMembers[index]["Checked"] = !arrayOfMembers[index]["Checked"];
            //Remove name from yLabels array if it's already there
            if (yLabels.includes(member["Username"].replace(/,/g, "."))){
                yLabels.splice(yLabels.indexOf(member["Username"].replace(/,/g, ".")), 1);
            }else{
                yLabels.push(member["Username"].replace(/,/g, "."));
            }
        }
    }
        
    document.querySelector("#scatterplot_div").innerHTML = '';
    scatterplot_div.remove();        
    scatterplot_div = d3.select("#scatterplot_div")
    .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
    .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        subMemberTimestamps = {};
        yLabels.forEach(name =>{
            subMemberTimestamps[name] = membersTimestamps[name];
        });
        
    //Remove "Testbot Online" and "Everyone" because they're added separately
    delete subMemberTimestamps["Testbot Online"];
    delete subMemberTimestamps["Everyone"];
    create_scatterplot(testbot_online_data_formatted, yLabels, subMemberTimestamps);
}

function render_checkboxes(member, box){
    let checkbox = document.createElement('input');
    //console.log(member);
    usernameOfMember = member["Username"].replace(/,/g, ".");    //The Firebase Realtime Database cannot have names with '.' in them.
    checkbox.setAttribute('type', "checkbox");
    checkbox.setAttribute('id', usernameOfMember);
    checkbox.setAttribute('name', usernameOfMember); 
    checkbox.setAttribute('class', 'checker'); 
    checkbox.checked = member["Checked"];
    
    
    let label = document.createElement('label');
    label.setAttribute("for", usernameOfMember);
    label.textContent = usernameOfMember;
    // TODO: May want to move the for loop to the outside
    
    checkbox.addEventListener("click", () => {
        render_data_points(member);
    }); 
    
    /* label.addEventListener("click", () => {
        render_data_points(member);
    }); */
    
    
    
    breaker = document.createElement('br');
    if (box == 0){
        checkbox_container1.appendChild(checkbox);
        checkbox_container1.appendChild(label);         
        checkbox_container1.appendChild(breaker);
        checkbox_container1.appendChild(breaker);
    }else if (box == 1){
        checkbox_container2.appendChild(checkbox);
        checkbox_container2.appendChild(label); 
        checkbox_container2.appendChild(breaker);
        checkbox_container2.appendChild(breaker);
    }else{
        checkbox_container3.appendChild(checkbox);
        checkbox_container3.appendChild(label); 
        checkbox_container3.appendChild(breaker);
        checkbox_container3.appendChild(breaker);
    }
    
}


var dbRefObject = database.ref('groupchatDatabase/CommentTimestampLog');

let activity_data = [];
let testbot_online_times = [];
let chartExists = false;
let yLabels = ["Testbot Online", "Everyone"];
let everyone_timestamps = [];
dbRefObject.once('value', (snapshot) => {
    
    let activity_data_raw = snapshot.val();
    
    activity_data = turnObjectIntoArray(activity_data_raw);
    
    //Changed to just sorting testbot_online_times, there may be some bug which means that wouldn't work
    //activity_data = sortTimeStampListArray(activity_data, "Timestamp");
    //console.log(activity_data);
    for (let index = 0;  index < (activity_data.length-1); index++){
        
        if (activity_data[index]["Username"] == "Testbot") {
            testbot_online_times.push(activity_data[index]);
        }else{
            //console.log(activity_data[index]["Username"])
            //console.log(membersTimestamps[activity_data[index]["Username"]]);
            if (activity_data[index]["Username"] in membersTimestamps){
                membersTimestamps[activity_data[index]["Username"]].push({"timestamp" : activity_data[index]["Timestamp"]});
                everyone_timestamps.push({"timestamp" : activity_data[index]["Timestamp"]});
            }
        }
        
    }
    testbot_online_times = sortTimeStampListArray(testbot_online_times, "Timestamp");
    //console.log(testbot_online_times)
    format_testbot_online_data(testbot_online_times);
    
    console.log(testbot_online_data_formatted);
    create_scatterplot(testbot_online_data_formatted, yLabels);
}); 



 // set the dimensions and margins of the graph
var margin = {top: 60, right: 60, bottom: 60, left: 200},
    width = 900 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

// append the svg object to the body of the page
// "g" is a g element that groups shapes together.
var scatterplot_div = d3.select("#scatterplot_div")
.append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
    .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


 // When reading the JSON, I must format date:
let dateParser = d3.timeParse("%d/%m/%Y %H:%M:%S");


let testbotActiveData = [];


// Add the line
function create_scatterplot(data, listOfNames, timeStamps = []) {
    console.log("Check2");
    // the x axis scale
    var xScale = d3.scaleTime()
        .domain([data[0].dates[0].date, data[data.length-1].dates[1].date])
        .range([ 0, width ])
        .nice();
    
    // the x axis 
    scatterplot_div.append("g")
        .attr("transform", "translate(0," + height + ")")
        .style("font", "24px times")
        .call(d3.axisBottom(xScale).ticks(5).tickSize(-innerHeight)); //.ticks(d3.timeDay.every(4))
    
    // the y axis scale    
    var yScale = d3.scalePoint()
        .range([ height, 0 ])
        .padding(0.4)
        .domain(listOfNames);
        
    // the y axis
    scatterplot_div.append("g")
        .style("font", "24px times")
        .call(d3.axisLeft(yScale));
    
    // the activity line
    data.forEach(dater => {
        scatterplot_div.append("path")
        .datum(dater.dates)
        .attr("fill", "none")
        .attr("stroke", "red")
        .attr("stroke-width", 1.5)
        .attr("d", d3.line()
            .x(function(d) {return xScale(d.date)})
            .y(yScale("Testbot Online"))
        );
    });
    
    // Everyone activity times
    
    
    scatterplot_div.selectAll('._Everyone').data(everyone_timestamps)
        .enter().append('circle')
            .attr('class', '_Everyone point')
            .attr('cy', yScale('Everyone'))
            .attr('cx', d => xScale(dateParser(d.timestamp)))
            .attr('r', 5)
            .style("fill", "#000");
    
    
    for (const timestamp in timeStamps){
        console.log("timeStamps");
        console.log(timeStamps);
        console.log("timestamp");
        console.log(timestamp);
        console.log("Timestamps[timestamp]: ");
        console.log(timeStamps[timestamp]);
        console.log("Timestamp yScale: ");
        console.log(yScale(timestamp));
        console.log("timeStamps[timestamp][2].timestamp");
        console.log(timeStamps[timestamp][0].timestamp);
        scatterplot_div.selectAll(`._${timestamp.replace(/\./g, '-')}`).data(timeStamps[timestamp])
        .enter().append('circle')
            .attr('class', `_${timestamp.replace(/\./g, '-')} point`)
            .attr('cy', yScale(timestamp))
            .attr('cx', d => xScale(dateParser(d.timestamp)))
            .attr('r', 5)
            .style("fill", "#000");
    }
    
    
        
}
//add_data_to_scatterplot(DUMMY_DATA2);


function add_points(data){
    
}

let testbot_online_data_formatted = [];
function format_testbot_online_data(testbot_online_times){
    
    
    for (let counter= 0; counter < testbot_online_times.length-1; counter += 2){
        
        testbot_online_data_formatted.push(
            {username: "testbot", 
            dates: [
                {date: dateParser(testbot_online_times[counter]["Timestamp"])}, 
                {date: dateParser(testbot_online_times[counter+1]["Timestamp"])},
                ]
            }
        );
    }
    
    if (testbot_online_times.length % 2 == 1){ //testbot_online_times[-1].online == "Start"){ I'll edit this in to work later
        let current_time_stamp = new Date();
        
        testbot_online_data_formatted.push(
            {value: 1, 
            dates: [
                {date: dateParser(testbot_online_times[testbot_online_times.length-1]["Timestamp"])}, 
                {date: current_time_stamp},
                ]
            }
        );
    }
}

function turnObjectIntoArray(object){  
    let objectArray = [];   
    for (let subObject in object){
        objectArray.push(object[subObject]);
    }
    
    return objectArray;
}

function sortTimeStampListArray(array, arrayField){
    array.sort(function(a, b){return dateParser(a[arrayField]) - dateParser(b[arrayField])});
    return array;
}

function sortMemberListArray(array, arrayField){
    if (arrayField == "Username"){
        array.sort(function(a, b){return a["Username"] > b["Username"] ? (1) : (-1)});
        return array;
    }else{
        array.sort(function(a, b){return b[arrayField] - a[arrayField]});
        return array;
    }
}

function removeAllChildNodes(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}