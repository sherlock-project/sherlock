# List Of Sites Removed From Sherlock

This is a list of sites implemented in such a way that the current design of
Sherlock is not capable of determining if a given username exists or not.
They are listed here in the hope that things may change in the future
so they may be re-included.


## Basecamp

As of 2020-02-23, all usernames are reported as not existing.

Why was this ever added?  It does not look like a social network.

```
  "Basecamp": {
    "errorMsg": "The account you were looking for doesn't exist",
    "errorType": "message",
    "rank": 4914,
    "url": "https://{}.basecamphq.com",
    "urlMain": "https://basecamp.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Fanpop

As of 2020-02-23, all usernames are reported as not existing.

```
  "fanpop": {
    "errorType": "response_url",
    "errorUrl": "http://www.fanpop.com/",
    "rank": 9454,
    "url": "http://www.fanpop.com/fans/{}",
    "urlMain": "http://www.fanpop.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewould_everusethis7"
  },
```

## Canva

As of 2020-02-23, all usernames are reported as not existing.

```
  "Canva": {
    "errorType": "response_url",
    "errorUrl": "https://www.canva.com/{}",
    "rank": 128,
    "url": "https://www.canva.com/{}",
    "urlMain": "https://www.canva.com/",
    "username_claimed": "jenny",
    "username_unclaimed": "xgtrq"
  },
```

## Pixabay

As of 2020-01-21, all usernames are reported as not existing.

```
  "Pixabay": {
    "errorType": "status_code",
    "rank": 378,
    "url": "https://pixabay.com/en/users/{}",
    "urlMain": "https://pixabay.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Pexels

As of 2020-01-21, all usernames are reported as not existing.

```
  "Pexels": {
    "errorType": "status_code",
    "rank": 745,
    "url": "https://www.pexels.com/@{}",
    "urlMain": "https://www.pexels.com/",
    "username_claimed": "bruno",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## RamblerDating

As of 2019-12-31, site always times out.

```
  "RamblerDating": {
    "errorType": "response_url",
    "errorUrl": "https://dating.rambler.ru/page/{}",
    "rank": 322,
    "url": "https://dating.rambler.ru/page/{}",
    "urlMain": "https://dating.rambler.ru/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## YandexMarket

As of 2019-12-31, all usernames are reported as existing.

```
  "YandexMarket": {
    "errorMsg": "\u0422\u0443\u0442 \u043d\u0438\u0447\u0435\u0433\u043e \u043d\u0435\u0442",
    "errorType": "message",
    "rank": 47,
    "url": "https://market.yandex.ru/user/{}/achievements",
    "urlMain": "https://market.yandex.ru/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Codementor

As of 2019-12-31, usernames that exist are not detected.

```
  "Codementor": {
    "errorType": "status_code",
    "rank": 10252,
    "url": "https://www.codementor.io/@{}",
    "urlMain": "https://www.codementor.io/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## KiwiFarms

As of 2019-12-31, the site gives a 403 for all usernames.  You have to
be logged into see a profile.

```
  "KiwiFarms": {
    "errorMsg": "The specified member cannot be found",
    "errorType": "message",
    "rank": 38737,
    "url": "https://kiwifarms.net/members/?username={}",
    "urlMain": "https://kiwifarms.net/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis"
  },
```

## Teknik

As of 2019-11-30, the site causes Sherlock to just hang.

```
  "Teknik": {
    "errorMsg": "The user does not exist",
    "errorType": "message",
    "rank": 357163,
    "url": "https://user.teknik.io/{}",
    "urlMain": "https://teknik.io/",
    "username_claimed": "red",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

## Shockwave

As of 2019-11-28, usernames that exist give a 503 "Service Unavailable"
HTTP Status.

```
  "Shockwave": {
    "errorMsg": "Oh no! You just finished all of the games on the internet!",
    "errorType": "message",
    "rank": 35916,
    "url": "http://www.shockwave.com/member/profiles/{}.jsp",
    "urlMain": "http://www.shockwave.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis"
  },
```

## Foursquare

Usernames that exist are not detected.

```
  "Foursquare": {
    "errorType": "status_code",
    "rank": 1843,
    "url": "https://foursquare.com/{}",
    "urlMain": "https://foursquare.com/",
    "username_claimed": "dens",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Khan Academy

Usernames that don't exist are detected.  First noticed 2019-10-25.

```
  "Khan Academy": {
    "errorType": "status_code",
    "rank": 377,
    "url": "https://www.khanacademy.org/profile/{}",
    "urlMain": "https://www.khanacademy.org/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## PayPal

Usernames that don't exist are detected.

```
  "PayPal": {
    "errorType": "response_url",
    "errorUrl": "https://www.paypal.com/paypalme2/404",
    "rank": 18441,
    "url": "https://www.paypal.com/paypalme2/{}",
    "urlMain": "https://www.paypal.me/",
    "username_claimed": "blue",
    "username_unclaimed": "noneownsthisusername"
  },
```

## EVE Online

Usernames that exist are not detected.

```
  "EVE Online": {
    "errorType": "response_url",
    "errorUrl": "https://eveonline.com",
    "rank": 15347,
    "url": "https://evewho.com/pilot/{}/",
    "urlMain": "https://eveonline.com",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## AngelList

Usernames that exist are not detected.

```
  "AngelList": {
    "errorType": "status_code",
    "rank": 5767,
    "url": "https://angel.co/{}",
    "urlMain": "https://angel.co/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Codepen

Usernames that exist are not detected.

```
  "Codepen": {
    "errorType": "status_code",
    "rank": 1359,
    "url": "https://codepen.io/{}",
    "urlMain": "https://codepen.io/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Imgur

Looks like they made some changes to the site.  Sherlock says that all
usernames are available.

```
  "Imgur": {
    "errorType": "status_code",
    "rank": 74,
    "url": "https://imgur.com/user/{}",
    "urlMain": "https://imgur.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## PowerShell Gallery

Accidentally merged even though the original pull request showed that all
user names were available.

```
  "PowerShell Gallery": {
    "errorType": "status_code",
    "rank": 163562,
    "url": "https://www.powershellgallery.com/profiles/{}",
    "urlMain": "https://www.powershellgallery.com",
    "username_claimed": "powershellteam",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## LinkedIn

This was attempted to be added around 2019-08-26, but the pull request was never merged.
It turns out that LinkedIn requires that you have an account before they will let you
check for other account.  So, this site will not work with the current design of
Sherlock.

## StreamMe

On 2019-04-07, I get a Timed Out message from the website.  It has not
been working earlier either (for some weeks).  It takes about 21s before
the site finally times out, so it really makes getting the results from
Sherlock a pain.

If the site becomes available in the future, we can put it back in.

```
  "StreamMe": {
    "errorType": "status_code",
    "rank": 31702,
    "url": "https://www.stream.me/{}",
    "urlMain": "https://www.stream.me/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## BlackPlanet

This site has always returned a false positive.  The site returns the exact
same text for a claimed or an unclaimed username.  The site must be rendering
all of the different content using Javascript in the browser.  So, there is
no way distinguish between the results with the current design of Sherlock.

```
  "BlackPlanet": {
    "errorMsg": "My Hits",
    "errorType": "message",
    "rank": 110021,
    "url": "http://blackplanet.com/{}",
    "urlMain": "http://blackplanet.com/"
  },
```

## Fotolog

Around 2019-02-09, I get a 502 HTTP error (bad gateway) for any access.  On
2019-03-10, the site is up, but it is in maintenance mode.

It does not seem to be working, so there is no sense in including it in
Sherlock.

```
  "Fotolog": {
    "errorType": "status_code",
    "rank": 47777,
    "url": "https://fotolog.com/{}",
    "urlMain": "https://fotolog.com/"
  },
```

## Google Plus

On 2019-04-02, Google shutdown Google Plus.  While the content for some
users is available after that point, it is going away.  And, no one will
be able to create a new account.  So, there is no value is keeping it in
Sherlock.

Good-bye [Google Plus](https://en.wikipedia.org/wiki/Google%2B)...

```
  "Google Plus": {
    "errorType": "status_code",
    "rank": 1,
    "url": "https://plus.google.com/+{}",
    "urlMain": "https://plus.google.com/",
    "username_claimed": "davidbrin1",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## CapFriendly

As of 2020-02-17, CapFriendly returns fake profile pages for non-existing users, what seems to distinguish between the pages is the Sign-up date, for non-existing users, the web application returns a date before 2000-01-01.

```
  "CapFriendly": {
    "errorMsg": "No User Found",
    "errorType": "message",
    "rank": 64100,
    "url": "https://www.capfriendly.com/users/{}",
    "urlMain": "https://www.capfriendly.com/",
    "username_claimed": "user",
    "username_unclaimed": "noonewouldeverusethis"
  },
```


## Furaffinity

As of 2020-02-23, Furaffinity returns false postives because they are now using Cloudflair, which prevents Sherlock from checking if the user
exists or not.

```
  "furaffinity": {
    "errorMsg": "user cannot be found",
    "errorType": "message",
    "rank": 0,
    "url": "https://www.furaffinity.net/user/{}",
    "urlMain": "https://www.furaffinity.net",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis777777"
  },
```


## InsaneJournal 

As of 2020-02-23, InsaneJournal returns false positive, when providing a username which contains a period.
Since we were not able to find the critera for a valid username, the best thing to do now is to remove it.

```
  "InsaneJournal": {
    "errorMsg": "Unknown user",
    "errorType": "message",
    "rank": 29728,
    "url": "http://{}.insanejournal.com/profile",
    "urlMain": "insanejournal.com",
    "username_claimed": "blue",
    "username_unclaimed": "dlyr6cd"
  },
```
