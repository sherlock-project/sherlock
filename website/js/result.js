// @author Miltos Tsichlis
//This js method takes the user name from the index page and allows to the user to use it
window.addEventListener('load', () => {


  
    const username = sessionStorage.getItem('USERNAME');
    
    document.getElementById('result-username').innerHTML = username;
  
  })