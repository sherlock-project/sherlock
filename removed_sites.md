# List Of Sites Removed From Sherlock

This is a list of sites implemented in such a way that the current design of
Sherlock is not capable of determining if a given username exists or not.
They are listed here in the hope that things may change in the future
so they may be re-included.

## Younow

Younow has changed their website (sometime before 2019-03-10) such that you
cannot see any user's profile unless you log in. So, it is now impossible to
probe for the existence of a username using the current strategy.

```
  "Younow": {
    "errorMsg": "pageTitle || 'YouNow - Broadcast Live",
    "errorType": "message",
    "rank": 13248,
    "url": "https://www.younow.com/{}",
    "urlMain": "https://www.younow.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  }
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
