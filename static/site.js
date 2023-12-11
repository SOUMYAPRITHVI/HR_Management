function gotEmployees(data) {
    console.log(data);
    $("#userdetails")[0].innerHTML=`<h1> Details for ${data.fname}  ${data.lname}</h1>
    <h2> ${data.title} </h2>
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
  <br><br>
    <h1>Add Leave Details</h1>
      <form action="/employees/${data.id}" method=post >
        <label for="leave_date">Leave Date</label>
        <input type="date" id="leavedate" name="leavedate"><br><br>
        <label for="leave_reason">Leave Reason</label>
        <input type="text" id="leavereason" name="leavereason"><br><br>
        <input type="submit" value="Submit">
        
    </form>
  
    </br>
  </br>
    `
}

$(function() {
    $("a.userlink").click(function (ev) {
        $.get(ev.target.href, gotEmployees);
        ev.preventDefault();
        });
});