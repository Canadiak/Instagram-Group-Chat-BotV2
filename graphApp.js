var database = firebase.database();

const activityTable = document.querySelector('#activity-table-body');
//const preObject = document.getElementById('object');

//create references

var dbRefObject = database.ref('groupchatDatabase/CommentTimestampLog');

let activity_data = [];
let testbot_online_times = []
let chartExists = false;
dbRefObject.once('value', (snapshot) => {
    
    let activity_data_raw = snapshot.val();
    
    activity_data = turnObjectIntoArray(activity_data_raw);
    
    activity_data = sortTimeStampListArray(activity_data, "Timestamp");
    //console.log(activity_data);
    for (let index = 0;  index < (activity_data.length-1); index++){
        
        if (activity_data[index]["Username"] == "Testbot") {
            testbot_online_times.push(activity_data[index]);
        }
    }
    
    //console.log(testbot_online_times)
    format_testbot_online_data(testbot_online_times);
    
    console.log(testbot_online_data_formatted);
    console.log(sampleData2);
    create_scatterplot(testbot_online_data_formatted);
}); 



 // set the dimensions and margins of the graph
var margin = {top: 10, right: 30, bottom: 30, left: 60},
    width = 460 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

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

let sampleData2 = [

    {username: 'testbot', dates : [
            {date: dateParser("14/03/2021 15:21:27")}, 
            {date: dateParser("14/03/2021 15:25:27")},
        ],
    },
    {username: 'testbot', dates : [
            {date: dateParser("14/03/2021 15:27:27")}, 
            {date: dateParser("14/03/2021 15:29:27")},
        ]
    },

];

//create_scatterplot(sampleData2);
// Add the line
function create_scatterplot(data) {
    var xScale = d3.scaleTime()
        //.domain(d3.extent(data, function(d) { return d.date; }))
        .domain([data[0].dates[0].date, data[data.length-1].dates[1].date])
        .range([ 0, width ])
        .nice();
    
    //domain([data[0].dates[0], data[data.length-1].dates[1]])
    //domain([dateParser("14/03/2021 15:21:27"), dateParser("14/03/2021 15:29:27")])
    scatterplot_div.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(xScale).ticks(d3.timeDay.every(4)));
        
    console.log(data);
    var yScale = d3.scaleLinear()
        .domain([0, 3])
        .range([ height, 0 ]);
  
    scatterplot_div.append("g")
        .call(d3.axisLeft(yScale));
    
    data.forEach(dater => {
        scatterplot_div.append("path")
        .datum(dater.dates)
        .attr("fill", "none")
        .attr("stroke", "red")
        .attr("stroke-width", 1.5)
        .attr("d", d3.line()
            .x(function(d) {return xScale(d.date)})
            .y(yScale(1))
        );
    });
   /*  scatterplot_div.append("path")
        .datum(data[0].dates)
        .attr("fill", "none")
        .attr("stroke", "red")
        .attr("stroke-width", 1.5)
        .attr("d", d3.line()
            .x(function(d) {return xScale(d.date)})
            .y(yScale(1))
        );
        
    scatterplot_div.append("path")
        .datum(data[1].dates)
        .attr("fill", "none")
        .attr("stroke", "green")
        .attr("stroke-width", 1.5)
        .attr("d", d3.line()
            .x(function(d) {return xScale(d.date)})
            .y(yScale(2))
        ); */
        
    /* scatterplot_div
        .data(data)
        .enter()
        .append('line')
        .style("stroke", "lightgreen")
        .style("stroke-width", 10)
        .attr('x1', xScale(data.date1))
        .attr('y1', yScale(1))
        .attr('x2', xScale(data.date2))
        .attr('y2', yScale(1))   */
        
    scatterplot_div.selectAll('circle').data(data)
    .enter().append('circle')
        .attr('cy', yScale(2))
        .attr('cx', xScale(20))
        .attr('r', 20); 

    scatterplot_div.selectAll('line').data(data)
    .enter().append('line')
        .attr('x1', xScale(dateParser("14/03/2021 15:21:27")))
        .attr('y1', yScale(1))
        .attr('x2', xScale(dateParser("14/03/2021 15:29:27")))
        .attr('y2', yScale(1));  
        
   /*  scatterplot_div.append('line')
        .style("stroke", "lightgreen")
        .style("stroke-width", 10)
        .attr('x1', xScale(dateParser("14/03/2021 15:21:27")))
        .attr('y1', yScale(3))
        .attr('x2', xScale(dateParser("14/03/2021 15:29:27")))
        .attr('y2', yScale(3));  */ 
        
    //console.log(data);
    /* data.forEach(datum => {
        console.log(datum);
        console.log(datum["date"]);
    }); */
              
}
//add_data_to_scatterplot(DUMMY_DATA2);

testbot_online_data_formatted = [];
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