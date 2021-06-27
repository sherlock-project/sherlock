// @author Miltos Tsichlis
// This js method passes the username on the session in order to be shown on the results page
function searchUsername () {
    const username = document.getElementById('username').value;

    
    sessionStorage.setItem("USERNAME", username);

    return;
}