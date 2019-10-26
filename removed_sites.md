# List Of Sites Removed From Sherlock

This is a list of sites implemented in such a way that the current design of
Sherlock is not capable of determining if a given username exists or not.
They are listed here in the hope that things may change in the future
so they may be re-included.


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

## Furaffinity

Usernames that don't exist are detected.

```
  "Furaffinity": {
    "errorMsg": "Fatal system error",
    "errorType": "message",
    "rank": 4278,
    "url": "https://www.furaffinity.net/user/{}",
    "urlMain": "https://www.furaffinity.net",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Duolingo

Usernames that don't exist are detected.

```
  "Duolingo": {
    "errorType": "response_url",
    "errorUrl": "https://www.duolingo.com/errors/404.html",
    "rank": 538,
    "regexCheck": "^[a-zA-Z0-9_-]{3,16}$",
    "url": "https://www.duolingo.com/{}",
    "urlMain": "https://www.duolingo.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewoulduse"
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
