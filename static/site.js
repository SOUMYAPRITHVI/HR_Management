function gotEmployees(data) {
    // console.log(data);
    $("#userdetails")[0].innerHTML=`<div><h1> Details for ${data.fname}  ${data.lname}</h1>
    <div><h3> ${data.title} </h3>
    <table>
      <tr>
        <th> First name </th>
        <td> ${data.fname}</td>
      </tr>
      <tr>
        <th> Last name </th>
        <td> ${data.lname}</td>
      </tr>
      <tr>
        <th> Email </th>
        <td> ${data.email}</td>
      </tr>
    <tr>
    <th> Phone </th>
    <td> ${data.phone}</td>
  </tr>
  <tr>
    <th >  Leave taken : </th>
    <td > ${data.leave}</td>
  </tr>
  <tr>
    <th> Maximum leave allowed : </th>
    <td> ${data.max_leaves}</td>
  </tr>
  <tr>
    <th>  Remaining leaves : </th>
    <td> ${data.leave_remain}</td>
  </tr>
</table>
<br>
<h3>Add Leave Details</h3>
  <form id="leaveForm" action="/employees/${data.id}" method=post >
    <label for="leave_date">Leave Date</label>
    <input type="date" id="leavedate" name="leavedate"><br><br>
    <label for="leave_reason">Leave Reason</label>
    <input type="text" id="leavereason" name="leavereason"><br><br>
    <input type="submit" id="submit" value="Submit">
    
</form>

</br>
    </div>
    `
}

$(function() {
    $("a.userlink").click(function (ev) {
        $.get(ev.target.href, gotEmployees);
        ev.preventDefault();
        });
});

// $(document).on("submit", "#leaveForm", function (event) {
//       event.preventDefault();
//       var leaveDate = $("#leavedate").val();
//       var leaveReason = $("#leavereason").val();
//       if (!leaveDate || !leaveReason) {
//         alert("Please fill in all fields.");
//         return;
//       }
//       var formData = $(this).serialize();
//       // console.log(formData)
//       $.ajax({
//         type: "POST",
//         url: $(this).attr("action"),
//         data: formData,
//         success: function (response) {
//           // console.log(response.body);
//           $("#leavedate").val("");
//           $("#leavereason").val("");
//           alert("Form submitted successfully");
//         },
//         error: function (error) {
//           console.log(error);
//           alert("Error submitting form", error);
//         }
//       });
//     })

    'use strict';
​
function Like() {
    const [text, setText] = React.useState('')
    const [state, setState] = React.useState([])
​
​
    const addItem= () => {
        if(!text) return
        setState((s) => [...s, {id: s.length, text: text}])
        setText('')
    }
    console.log(state)
    return(<div>
        Enter text: <input type="text" value={text} onChange={(e) => setText(e.target.value)} /><br/>
        <button onClick={addItem}>Add</button>
        <ul>
        {state.map(({id, text}) => <li key={id}>{text}</li>)}
        </ul>
    </div>)
​
}
​
const domContainer = document.getElementById('userdetails');
const root = ReactDOM.createRoot(domContainer);
root.render(React.createElement(gotEmployees));