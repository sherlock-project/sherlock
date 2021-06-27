window.addEventListener('load', () => {


  
    const username = sessionStorage.getItem('USERNAME');
    
    document.getElementById('result-username').innerHTML = username;
  
  })