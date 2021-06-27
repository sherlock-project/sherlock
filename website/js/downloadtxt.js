let saveResults = () => {
    const username = sessionStorage.getItem('USERNAME');
    
    let data = 
    '\r Results for username: ' + username + ' \r\n ' +
    'This file will contain all the urls of your search.' +  ' \r\n ' +
    '9GAG: https://www.9gag.com/u/miltos04' +  ' \r\n ' +
    'AskFM: https://ask.fm/miltos04' +  ' \r\n ' +
    'FortniteTracker: https://fortnitetracker.com/profile/all/miltos04' +  ' \r\n ' +
    'GitHub: https://www.github.com/miltos04' +  ' \r\n ' +
    'Gravatar: http://en.gravatar.com/miltos04' +  ' \r\n ' +
    'Periscope: https://www.periscope.tv/miltos04/' +  ' \r\n ' +
    'Reddit: https://www.reddit.com/user/miltos04' +  ' \r\n ' +
    'Repl.it: https://repl.it/@miltos04' +  ' \r\n ' +
    'Roblox: https://www.roblox.com/user.aspx?username=miltos04' +  ' \r\n ' +
    'Scribd: https://www.scribd.com/miltos04' +  ' \r\n ' +
    'TikTok: https://tiktok.com/@miltos04' +  ' \r\n ' +
    'Twitch: https://www.twitch.tv/miltos04';

    const textToBLOB = new Blob([data], { type: 'text/plain' });
    const sFileName = username +'.txt';	   // The file to save the data.

    let newLink = document.createElement("a");
    newLink.download = sFileName;

    if (window.webkitURL != null) {
        newLink.href = window.webkitURL.createObjectURL(textToBLOB);
    }
    else {
        newLink.href = window.URL.createObjectURL(textToBLOB);
        newLink.style.display = "none";
        document.body.appendChild(newLink);
    }

    newLink.click(); 
}
