// Note: I get warnings from JSDoc for putting @type and descriptions on the same line, but it works fine
/** 
 * Database parent node. Each group chat has its own parent node, so each site references a different node.
 * databaseName should be the only different value across sites.
 * @type {string}
 */
const databaseName = "groupchatDatabase";
const database = firebase.database();
const activityTable = document.querySelector('#activity-table-body');
/** @type {database.ref} - The database reference to where count of each member's messages is stored */
namesRefObject = database.ref(databaseName + "/Members");
/** @type {array.<object>} - The array of objects that contain data about # of messages from each member */
let arrayOfMembers = [];
/** @type {object.<member_username: <array>>} - An object that contains lists of timestamps for each member, keyed to their username.*/
let membersTimestamps = {};
namesRefObject.once('value', (snapshot) => {
  let memberList = snapshot.val();
  arrayOfMembers = turnObjectIntoArray(/* object= */ memberList);
  
  for (const memberer of arrayOfMembers){
    memberer["Checked"] = false;
    membersTimestamps[memberer["Username"].replace(/,/g, ".")] = [];
  }
  
  removeAllChildNodes(/* parent= */ checkboxContainer1);
  removeAllChildNodes(/* parent= */ checkboxContainer2);
  removeAllChildNodes(/* parent= */ checkboxContainer3);
  putMembersInDivs(/* arrayOfMembers= */ arrayOfMembers, /* field= */ "Message_Count");
  boxSorter.value = "Sort Alphabetically";
});

checkboxContainer1 = document.querySelector('#con1');
checkboxContainer2 = document.querySelector('#con2');
checkboxContainer3 = document.querySelector('#con3');

/**
  * Creates the field of checkboxes from the array of members
  * @param {array.<object>} arrayOfMembers The array of objects of members and their # of comments
  * @param {integer} field The number of the field to sort arrayOfMembers by
  * @returns {void} 
  */  
function putMembersInDivs(arrayOfMembers, field){
  let sortedArray = sortMemberListArray(arrayOfMembers, field);
  for (const [index, member] of sortedArray.entries()){
    renderCheckbox(member, index % 3);
  }
}

boxSorter = document.querySelector(".box-sorter");
// Adds the event listener to the sort button so the checkboxes can be sorted by # of messages or alphabetically
boxSorter.addEventListener("click", () =>{
  if (boxSorter.value === "Sort Alphabetically"){
    removeAllChildNodes(/* parent=*/ checkboxContainer1);
    removeAllChildNodes(/* parent=*/ checkboxContainer2);
    removeAllChildNodes(/* parent=*/ checkboxContainer3);
    putMembersInDivs(arrayOfMembers, "Username");
    boxSorter.value = "Sort by Message Count";
  }else{
    removeAllChildNodes(checkboxContainer1);
    removeAllChildNodes(checkboxContainer2);
    removeAllChildNodes(checkboxContainer3);
    putMembersInDivs(/* arrayOfMembers= */ arrayOfMembers, /* field= */ "Message_Count");
    boxSorter.value = "Sort Alphabetically";
  }
});

/**
  * Adds a member to the list of members to render, then destroys and recreates the timestamp scatterplot.
  * @param {object} member An object of {Message_count: integer, Username: username}. 
  * @returns {void} 
  */
function renderDataPoints(member){
  // Switches the property of member that holds whether their checkbox is checked
  member["Checked"] = !member["Checked"];
  //Remove name from yLabels array that tracks who should be rendered if it's already there
  if (yLabels.includes(member["Username"].replace(/,/g, "."))){
    yLabels.splice(yLabels.indexOf(member["Username"].replace(/,/g, ".")), 1);
  }else{
    yLabels.push(member["Username"].replace(/,/g, "."));
  }
  
  // Clears the timestamp scatterplot and recreates it
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
  createScatterplot(testbotOnlineDataFormatted, yLabels, subMemberTimestamps);
}

/**
  * Renders each checkbox 
  * @param {object} member An object of {Message_count: integer, Username: username}. 
  * @param {integer} box The number of the checkbox container div that 
  * @returns {void} 
  */
function renderCheckbox(member, box){
  let checkbox = document.createElement('input');
  //console.log(member);
  usernameOfMember = member["Username"].replace(/,/g, ".");  //The Firebase Realtime Database cannot have names with '.' in them.
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
    renderDataPoints(member);
  }); 
  
  breaker = document.createElement('br');
  if (box === 0){
    checkboxContainer1.appendChild(checkbox);
    checkboxContainer1.appendChild(label);     
    checkboxContainer1.appendChild(breaker);
    checkboxContainer1.appendChild(breaker);
  }else if (box === 1){
    checkboxContainer2.appendChild(checkbox);
    checkboxContainer2.appendChild(label); 
    checkboxContainer2.appendChild(breaker);
    checkboxContainer2.appendChild(breaker);
  }else{
    checkboxContainer3.appendChild(checkbox);
    checkboxContainer3.appendChild(label); 
    checkboxContainer3.appendChild(breaker);
    checkboxContainer3.appendChild(breaker);
  }
}

let dbRefObject = database.ref(databaseName + '/CommentTimestampLog');
let activityData = [];
let testbotOnlineTimes = [];
let chartExists = false;
let yLabels = ["Testbot Online", "Everyone"];
let everyoneTimestamps = [];
let hourData = [];
let data = {};
for (let index = 0; index < 24; index++){
  hourData.push({
    "Message_Count" : 0,
    "Hour" : (index).toString(),
  });
}

// Creates the activity scatterplot and the myChart with the # of messages at each hour
dbRefObject.once('value', (snapshot) => {
  
  let activityData_raw = snapshot.val();
  activityData = turnObjectIntoArray(/* object= */ activityData_raw);
  
  for (const act_datum of activityData){
    if (act_datum["Username"] === "Testbot") {
      testbotOnlineTimes.push(act_datum);
    }else{
      if (act_datum["Username"] in membersTimestamps){
        membersTimestamps[act_datum["Username"]].push({"timestamp" : act_datum["Timestamp"]});
        everyoneTimestamps.push({"timestamp" : act_datum["Timestamp"]});
      }
    } 
    hourData[dateParser(act_datum["Timestamp"]).getHours()]["Message_Count"]++;
  }
  testbotOnlineTimes = sortTimeStampListArray(testbotOnlineTimes, "Timestamp");
  formatTestbotOnlineData(testbotOnlineTimes);
  createScatterplot(testbotOnlineDataFormatted, yLabels);
  
  // My Chart Code //
  data = createData(hourData);
  console.log("Data: ");
  console.log(data);
  activityGraph = new Chart(myChart, data);
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
const dateParser = d3.timeParse("%d/%m/%Y %H:%M:%S");

let testbotActiveData = [];

// Add the line
function createScatterplot(data, listOfNames, timeStamps = []) {
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
  scatterplot_div.selectAll('._Everyone').data(everyoneTimestamps)
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
      .attr('r', 5) // Radius of each point
      .style("fill", "#000");
  }
}

let testbotOnlineDataFormatted = [];
function formatTestbotOnlineData(testbotOnlineTimes){
  // TODO: Maybe convert to a for...of loop?
  for (let counter= 0; counter < testbotOnlineTimes.length-1; counter += 2){
    testbotOnlineDataFormatted.push(
      {username: "testbot", 
      dates: [
        {date: dateParser(testbotOnlineTimes[counter]["Timestamp"])}, 
        {date: dateParser(testbotOnlineTimes[counter+1]["Timestamp"])},
        ]
      }
    );
  }
  if (testbotOnlineTimes.length % 2 === 1){ 
    let current_time_stamp = new Date();
    testbotOnlineDataFormatted.push(
      {value: 1, 
      dates: [
        {date: dateParser(testbotOnlineTimes[testbotOnlineTimes.length-1]["Timestamp"])}, 
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
  if (arrayField === "Username"){
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



//    -------------    //
//    MY CHART CODE    //
//    -------------    //


var myChart = document.getElementById('my-chart').getContext('2d');

//Global Options
Chart.defaults.global.defaultFontFamily ='Lato';
Chart.defaults.global.defaultFontSize = 18;
Chart.defaults.global.defaultFontColor = '#777';


function createData (rawData){
  
  numOfCommentsList = [];
  names_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", ];
  colourList = [];
  console.log("Raw data: ");
  console.log(rawData);
  sumOfMessages = 0;
  rawData.forEach(item => {
    sumOfMessages += item["Message_Count"];
  });
  
  for(let index = 0; index < 24; index++){
    numOfCommentsList.push(rawData[index]["Message_Count"]);
    hue = index * (360/24);
    colourList.push(`hsla(${hue}, 70%, 70%, 0.8`);
  }
  
  formattedData = {
  
    type: 'bar', //bar, horizontalBar, pie, line, doughnut, radar, polarArea
    
    data: {
      labels: names_list,
      datasets:[{
        label:"Number of Messages",
        data: numOfCommentsList,
        //backgroundColor:'green'
        backgroundColor: colourList,
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

