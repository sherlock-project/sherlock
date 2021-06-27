function searchUsername () {
    const username = document.getElementById('username').value;

    
    sessionStorage.setItem("USERNAME", username);

    return;
}