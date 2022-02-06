# List Of Sites Removed From Sherlock

This is a list of sites implemented in such a way that the current design of
Sherlock is not capable of determining if a given username exists or not.
They are listed here in the hope that things may change in the future
so they may be re-included.


## gpodder.net

As of 2020-05-25, all usernames are reported as available.

The server is returning a HTTP Status 500 (Internal server error)
for all queries.

```
  "gpodder.net": {
    "errorType": "status_code",
    "rank": 2013984,
    "url": "https://gpodder.net/user/{}",
    "urlMain": "https://gpodder.net/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```


## Investing.com

As of 2020-05-25, all usernames are reported as claimed.

Any query against a user seems to be redirecting to a general
information page at https://www.investing.com/brokers/.  Probably
required login before access.

```
  "Investing.com": {
    "errorType": "status_code",
    "rank": 196,
    "url": "https://www.investing.com/traders/{}",
    "urlMain": "https://www.investing.com/",
    "username_claimed": "jenny",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## AdobeForums

As of 2020-04-12, all usernames are reported as available.

When I went to the site to see what was going on, usernames that I know
existed were redirecting to the main page.

I was able to see user profiles without logging in, but the URL was not
related to their user name.  For example, user "tomke" went to
https://community.adobe.com/t5/user/viewprofilepage/user-id/10882613.
This can be detected, but it requires a different detection method.

```
  "AdobeForums": {
    "errorType": "status_code",
    "rank": 59,
    "url": "https://forums.adobe.com/people/{}",
    "urlMain": "https://forums.adobe.com/",
    "username_claimed": "jack",
    "username_unclaimed": "noonewouldeverusethis77777"
  },
```

## Basecamp

As of 2020-02-23, all usernames are reported as not existing.


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

## NPM-Packages

NPM-Packages are not users.

```
  "NPM-Package": {
    "errorType": "status_code",
    "url": "https://www.npmjs.com/package/{}",
    "urlMain": "https://www.npmjs.com/",
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

When usage of automated tool is detected. Whole IP is banned from future requests.
There is an error message:

> Please verify you are a human
> Access to this page has been denied because we believe you are using automation tools to browse the website.

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

Usernames that exist are not detected. Forbidden Request 403 Error.

```
  "AngelList": {
    "errorType": "status_code",
    "rank": 5767,
    "url": "https://angel.co/u/{}",
    "urlMain": "https://angel.co/",
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

## Sports Tracker

As of 2020-04-02, Sports Tracker returns false positives. Checking with `errorMsg` and `response_url`
did not seem to work.

```
   "SportsTracker": {
     "errorUrl": "https://www.sports-tracker.com/page-not-found",
     "errorType": "response_url",
     "rank": 93950,
     "url": "https://www.sports-tracker.com/view_profile/{}",
     "urlMain": "https://www.sports-tracker.com/",
     "username_claimed": "blue",
     "username_unclaimed": "noonewouldeveruse"
   },
```

## Trip

As of 2020-04-02, Trip by Skyscanner seems to not work beceause it keeps on
redirecting to skyscanner.com whether the username exists or not.

```
  "Trip": {
      "errorType": "status_code",
      "rank": 2847,
      "url": "https://www.trip.skyscanner.com/user/{}",
      "urlMain": "https://www.trip.skyscanner.com/",
      "username_claimed": "blue",
      "username_unclaimed": "noonewouldeverusethis7"
  },

```

## boingboing.net

As of 2020-04-02, boingboing.net requires a login to check if a user exits or not.

```
   "boingboing.net": {
     "errorType": "status_code",
     "rank": 5821,
     "url": "https://bbs.boingboing.net/u/{}",
     "urlMain": "https://boingboing.net/",
     "username_claimed": "admin",
     "username_unclaimed": "noonewouldeverusethis7"
   },
```

## elwoRU
As of 2020-04-04, elwoRu does not exist anymore. I confirmed using
downforeveryoneorjustme.com that the website is down.

```
  "elwoRU": {
    "errorMsg": "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d",
    "errorType": "message",
    "rank": 254810,
    "url": "https://elwo.ru/index/8-0-{}",
    "urlMain": "https://elwo.ru/",
    "username_claimed": "red",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## ingvarr.net.ru

As of 2020-04-04, ingvarr.net.ru does not exist anymore. I confirmed using
downforeveryoneorjustme.com that the website is down.

```
  "ingvarr.net.ru": {
    "errorMsg": "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d",
    "errorType": "message",
    "rank": 107721,
    "url": "http://ingvarr.net.ru/index/8-0-{}",
    "urlMain": "http://ingvarr.net.ru/",
    "username_claimed": "red",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Redsun.tf

As of 2020-06-20, Redsun.tf seems to be adding random digits to the end of the usernames which makes it pretty much impossible
for Sherlock to check for usernames on this particular website.

```
  "Redsun.tf": {
    "errorMsg": "The specified member cannot be found",
    "errorType": "message",
    "rank": 3796657,
    "url": "https://forum.redsun.tf/members/?username={}",
    "urlMain": "https://redsun.tf/",
    "username_claimed": "dan",
    "username_unclaimed": "noonewouldeverusethis"
  },
```

## Creative Market

As of 2020-06-20, Creative Market has a captcha to prove that you are a human, and because of this
Sherlock is unable to check for username on this site because we will always get  a page which asks
us to prove that we are not a robot.

```
  "CreativeMarket": {
    "errorType": "status_code",
    "rank": 1896,
    "url": "https://creativemarket.com/users/{}",
    "urlMain": "https://creativemarket.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## pvpru

As of 2020-06-20, pvpru uses CloudFlair, and because of this we get a "Access denied" error whenever
we try to check for a username.

```
  "pvpru": {
    "errorType": "status_code",
    "rank": 405547,
    "url": "https://pvpru.com/board/member.php?username={}&tab=aboutme#aboutme",
    "urlMain": "https://pvpru.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## easyen
As of 2020-06-21, easyen returns false positives when using a username which contains
a period. Since we could not find the criteria for the usernames for this site, it will be
removed

```
  "easyen": {
    "errorMsg": "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d",
    "errorType": "message",
    "rank": 11564,
    "url": "https://easyen.ru/index/8-0-{}",
    "urlMain": "https://easyen.ru/",
    "username_claimed": "wd",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## pedsovet
As of 2020-06-21, pedsovet returns false positives when using a username which contains
a period. Since we could not find the criteria for the usernames for this site, it will be
removed

```
  "pedsovet": {
    "errorMsg": "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d",
    "errorType": "message",
    "rank": 6776,
    "url": "http://pedsovet.su/index/8-0-{}",
    "urlMain": "http://pedsovet.su/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```


## radioskot
As of 2020-06-21, radioskot returns false positives when using a username which contains
a period. Since we could not find the criteria for the usernames for this site, it will be
removed
```
  "radioskot": {
    "errorMsg": "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d",
    "errorType": "message",
    "rank": 105878,
    "url": "https://radioskot.ru/index/8-0-{}",
    "urlMain": "https://radioskot.ru/",
    "username_claimed": "red",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```



## Coderwall
As of 2020-07-06, Coderwall returns false positives when checking for an username which contains a period.
I have tried to find out what Coderwall's criteria is for a valid username, but unfortunetly I have not been able to 
find it and because of this, the best thing we can do now is to remove it.
```
  "Coderwall": {
    "errorMsg": "404! Our feels when that url is used",
    "errorType": "message",
    "rank": 11256,
    "url": "https://coderwall.com/{}",
    "urlMain": "https://coderwall.com/",
    "username_claimed": "jenny",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```


## TamTam
As of 2020-07-06, TamTam returns false positives when given a username which contains a period
```
  "TamTam": {
    "errorType": "response_url",
    "errorUrl": "https://tamtam.chat/",
    "rank": 87903,
    "url": "https://tamtam.chat/{}",
    "urlMain": "https://tamtam.chat/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Zomato
As of 2020-07-24, Zomato seems to be unstable. Majority of the time, Zomato takes a very long time to respond.
```
  "Zomato": {
    "errorType": "status_code",
    "headers": {
      "Accept-Language": "en-US,en;q=0.9"
    },
    "rank": 1920,
    "url": "https://www.zomato.com/pl/{}/foodjourney",
    "urlMain": "https://www.zomato.com/",
    "username_claimed": "deepigoyal",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Mixer
As of 2020-07-22, the Mixer service has closed down.
```
  "mixer.com": { 
    "errorType": "status_code", 
    "rank": 1544, 
    "url": "https://mixer.com/{}", 
    "urlMain": "https://mixer.com/", 
    "urlProbe": "https://mixer.com/api/v1/channels/{}", 
    "username_claimed": "blue", 
    "username_unclaimed": "noonewouldeverusethis7" 
  }, 
```


## KanoWorld
As of 2020-07-22, KanoWorld's api.kano.me subdomain no longer exists which makes it not possible for us check for usernames.
If an alternative way to check for usernames is found then it will added.
```
  "KanoWorld": {
    "errorType": "status_code",
    "rank": 181933,
    "url": "https://api.kano.me/progress/user/{}",
    "urlMain": "https://world.kano.me/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## YandexCollection
As of 2020-08-11, YandexCollection presents us with a rechapta which prevents us from checking for usernames
```
  "YandexCollection": {
    "errorType": "status_code",
    "url": "https://yandex.ru/collections/user/{}/",
    "urlMain": "https://yandex.ru/collections/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## PayPal

As of 2020-08-24, PayPal now returns false positives, which was found when running the tests, but will most likley be added again in the near
future once we find a better error detecting method.
```
  "PayPal": {
    "errorMsg": "<meta name=\"twitter:title\" content=\"Get your very own PayPal.Me link\" />",
    "errorType": "message",
    "url": "https://www.paypal.com/paypalme/{}",
    "headers": {
      "User-Agent": ""
    },
    "urlMain": "https://www.paypal.me/",
    "username_claimed": "blue",
    "username_unclaimed": "noneownsthisusername7"
  },
```

## ImageShack

As of 2020-08-24, ImageShack now returns false positives, which was found when running the tests, but will most likley be added again in the near future once we find a better error detecting method.
```
  "ImageShack": {
    "errorType": "response_url",
    "errorUrl": "https://imageshack.us/",
    "url": "https://imageshack.us/user/{}",
    "urlMain": "https://imageshack.us/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Aptoide

As of 2020-08-24, Aptoide now returns false positives, which was found when running the tests, but will most likley be added again in the near
future once we find a better error detecting method.
```
  "Aptoide": {
    "errorType": "status_code",
    "url": "https://{}.en.aptoide.com/",
    "urlMain": "https://en.aptoide.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Crunchyroll

As of 2020-08-24, Crunchyroll now returns false positives, which was found when running the tests, but will most likley be added again in the near future once we find a better error detecting method.

```
  "Crunchyroll": {
    "errorType": "status_code",
    "url": "https://www.crunchyroll.com/user/{}",
    "urlMain": "https://www.crunchyroll.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## T-MobileSupport
As of 2020-08-24, T-MobileSupport now returns false positives, which was found when running the tests, but will most likley be added again in the near future once we find a better error detecting method.

```
  "T-MobileSupport": {
    "errorType": "status_code",
    "url": "https://support.t-mobile.com/people/{}",
    "urlMain": "https://support.t-mobile.com",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## OpenCollective

As of 2020-08-24, OpenCollective now returns false positives, which was found when running the tests, but will most likley be added again in the near future once we find a better error detecting method.

```
  "OpenCollective": {
    "errorType": "status_code",
    "url": "https://opencollective.com/{}",
    "urlMain": "https://opencollective.com/",
    "username_claimed": "sindresorhus",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## SegmentFault

As of 2020-08-24, SegmentFault now returns false positives, which was found when running the tests, but will most likley be added again in the near future once we find a better error detecting method.

```
  "SegmentFault": {
    "errorType": "status_code",
    "url": "https://segmentfault.com/u/{}",
    "urlMain": "https://segmentfault.com/",
    "username_claimed": "bule",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Viadeo

As of 2020-08-24, Viadeo now returns false positives, which was found when running the tests, but will most likley be added again in the near future once we find a fix for this

```
  "Viadeo": {
    "errorType": "status_code",
    "url": "http://fr.viadeo.com/en/profile/{}",
    "urlMain": "http://fr.viadeo.com/en/",
    "username_claimed": "franck.patissier",
    "username_unclaimed": "noonewouldeverusethis"
  },
```

## MeetMe

As of 2020-09-02, MeetMe returns false positives

```
  "MeetMe": {
    "errorType": "response_url",
    "errorUrl": "https://www.meetme.com/",
    "url": "https://www.meetme.com/{}",
    "urlMain": "https://www.meetme.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Linkdedin

As of 2020-09-23, Linkedin returns false positives because we are prompted with prompted to login when checking for a user

```
  "Linkedin": {
    "errorMsg": "could not be found",
    "errorType": "message",
    "rank": 0,
    "url": "https://www.linkedin.com/in/{}",
    "urlMain": "https://www.linkedin.com/",
    "username_claimed": "alex",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## tracr.co
As of 2020-09-23, tracr.co returns false positives because the site seems to be shut down.
```
  "tracr.co": {
    "errorMsg": "No search results",
    "errorType": "message",
    "regexCheck": "^[A-Za-z0-9]{2,32}$",
    "url": "https://tracr.co/users/1/{}",
    "urlMain": "https://tracr.co/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

## Taringa

As of 2020-09-23, Taringa returns false positives.

```
  "Taringa": {
    "errorType": "status_code",
    "regexCheck": "^[^.]*$",
    "url": "https://www.taringa.net/{}",
    "urlMain": "https://taringa.net/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Photobucket
As of 2020-10-21, Photobucket return false positives. This was reported in #785.
```
  "Photobucket": {
    "errorType": "status_code",
    "url": "https://photobucket.com/user/{}/library",
    "urlMain": "https://photobucket.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## 4PDA
As of 2020-10-21, 4PDA returns false positives. This was reported in #784.

```
  "4pda": {
    "errorMsg": "[1,false,0]",
    "errorType": "message",
    "url": "https://4pda.ru/forum/index.php?act=search&source=pst&noform=1&username={}",
    "urlMain": "https://4pda.ru/",
    "urlProbe": " https://4pda.ru/forum/index.php?act=auth&action=chkname&login={}",
    "username_claimed": "green",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## PokerStrategy
As of 2020-10-21, PokerStrategy returns false positives. This was reported in #776.
```
  "PokerStrategy": {
    "errorType": "status_code",
    "url": "http://www.pokerstrategy.net/user/{}/profile/",
    "urlMain": "http://www.pokerstrategy.net",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Filmogs

Filmogs has closed down.

> **Filmogs is closed**
> **31-Aug 2020** - We are preparing the last data export and collection of images. It will be published here by 19-Oct 2020. If you have requested an export of your data it will also be emailed to you by 19-Oct 2020.

```
  "Filmogs": {
    "errorType": "status_code",
    "url": "https://www.filmo.gs/users/{}",
    "urlMain": "https://www.filmo.gs/",
    "username_claimed": "cupparober",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## 500px
As of 2021-01-13, 500px returns false positives. This will hopefully be fixed soon once we add the ability to add different
request methods.

```
  "500px": {
    "errorMsg": "No message available",
    "errorType": "message",
    "url": "https://500px.com/p/{}",
    "urlMain": "https://500px.com/",
    "urlProbe": "https://api.500px.com/graphql?operationName=ProfileRendererQuery&variables=%7B%22username%22%3A%22{}%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%224d02ff5c13927a3ac73b3eef306490508bc765956940c31051468cf30402a503%22%7D%7D",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Badoo
As of 2021-01-13, Badoo returns false positives
```
  "Badoo": {
    "errorType": "status_code",
    "url": "https://badoo.com/profile/{}",
    "urlMain": "https://badoo.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Pling
As of 2021-01-13, Pling returns false positives.
```
  "Pling": {
    "errorMsg": "Resource not found",
    "errorType": "message",
    "url": "https://www.pling.com/u/{}/",
    "urlMain": "https://www.pling.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis"
  },
```

## Realmeye
As of 2021-01-13, Realmeye returns false positives.
```
  "Realmeye": {
    "errorMsg": "Sorry, but we either:",
    "errorType": "message",
    "url": "https://www.realmeye.com/player/{}",
    "urlMain": "https://www.realmeye.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Travellerspoint
As of 2021-01-13, Travellerspoint returns false positives
```
  "Travellerspoint": {
    "errorMsg": "Wooops. Sorry!",
    "errorType": "message",
    "url": "https://www.travellerspoint.com/users/{}",
    "urlMain": "https://www.travellerspoint.com",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Ebay

As of 2021-01-15, Ebay seems to be very laggy and take too long to return a response.
```
  "Ebay": {
    "errorMsg": "<title>eBay Profile - error</title>",
    "errorType": "message",
    "url": "https://www.ebay.com/usr/{}",
    "urlMain": "https://www.ebay.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## GDProfiles

As of 2021-06-27, GDProfiles takes way too long to respond. Must be an issue on their side.
```
  "GDProfiles": {
    "errorType": "status_code",
    "url": "https://gdprofiles.com/{}",
    "urlMain": "https://gdprofiles.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis"
  },
```

## AllTrails

As of 2021-06-27, AllTrails has a chapta which prevents us from checking for usernames on the site.
```
  "AllTrails": {
    "errorMsg": "class=\"home index\"",
    "errorType": "message",
    "url": "https://www.alltrails.com/members/{}",
    "urlMain": "https://www.alltrails.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis"
  }
```

## Cent

As of 2021-06-27, there is not way of checking if a username exists on Cent

```
  "Cent": {
    "errorMsg": "<title>Cent</title>",
    "errorType": "message",
    "url": "https://beta.cent.co/@{}",
    "urlMain": "https://cent.co/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Anobii

As of 2021-06-27, Anobii returns false positives and there is no stable way of checking usernames.
```

  "Anobii": {
    "errorType": "response_url",
    "url": "https://www.anobii.com/{}/profile",
    "urlMain": "https://www.anobii.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

## Kali Community

As of 2021-06-27, Kali Community requires us to be logged in order to check if a user exists on their forum.

```
  "Kali community": {
    "errorMsg": "This user has not registered and therefore does not have a profile to view.",
    "errorType": "message",
    "url": "https://forums.kali.org/member.php?username={}",
    "urlMain": "https://forums.kali.org/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

## NameMC

As of 2021-06-27, NameMC uses chapta through CloudFlare which prevents us from checking if usernames exists on the site.

```
  "NameMC (Minecraft.net skins)": {
    "errorMsg": "Profiles: 0 results",
    "errorType": "message",
    "url": "https://namemc.com/profile/{}",
    "urlMain": "https://namemc.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## SteamID

As of 2021-06-27, Steam uses chapta through CloudFlare which prevents us from checking if usernames exists on the site.
```
  "Steamid": {
    "errorMsg": "<link rel=\"canonical\" href=\"https://steamid.uk\" />",
    "errorType": "message",
    "url": "https://steamid.uk/profile/{}",
    "urlMain": "https://steamid.uk/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```


## TripAdvisor

As of 2021-06-27, Trip takes too long to return a response. As of now, the reason is not known.
```
  "TripAdvisor": {
    "errorMsg": "This page is on vacation\u2026",
    "errorType": "message",
    "url": "https://tripadvisor.com/members/{}",
    "urlMain": "https://tripadvisor.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },

```

## YouTube

As of 2021-06-27, there is no way of checking if a username exists on YouTube. We'll have to take a deeper look
into this as YouTube is must have site in Sherlock.

```
  "YouTube": {
    "errorMsg": "This page isn't available",
    "errorType": "message",
    "url": "https://www.youtube.com/{}",
    "urlMain": "https://www.youtube.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

### House Mixes

As of 2021-09-04, House Mixes has issues connecting causing Sherlock to freeze.
```
  "House-Mixes.com": {
    "errorMsg": "Profile Not Found",
    "errorType": "message",
    "regexCheck": "^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$",
    "url": "https://www.house-mixes.com/profile/{}",
    "urlMain": "https://www.house-mixes.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

### Quora
As of 2021-09-04, Quora returns false positives.
```
  "Quora": {
    "errorMsg": "Page Not Found",
    "errorType": "message",
    "url": "https://www.quora.com/profile/{}",
    "urlMain": "https://www.quora.com/",
    "username_claimed": "Matt-Riggsby",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

### SparkPeople
As of 2021-09-04, SparkPeople returns false positives.
```
  "SparkPeople": {
    "errorMsg": "We couldn't find that user",
    "errorType": "message",
    "url": "https://www.sparkpeople.com/mypage.asp?id={}",
    "urlMain": "https://www.sparkpeople.com",
    "username_claimed": "adam",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

### Cloob
As of 2021-10-25, Cloob seems to be down and their site is not responding.
```
  "Cloob": {
    "errorType": "status_code",
    "url": "https://www.cloob.com/name/{}",
    "urlMain": "https://www.cloob.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

### 1337x
As of 2021-11-21, 1337x seems to be down causing false positives.
```
  "1337x": {
    "errorMsg": "Bad Username",
    "errorType": "message",
    "url": "https://1337x.to/user/{}/",
    "urlMain": "https://1337x.to",
    "username_claimed": "TheMorozko",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

### TM-Ladder
As of 2021-11-30, TM-Ladder is returning false positives due to rate limits.

```
  "TM-Ladder": {
    "errorMsg": "player unknown or invalid",
    "errorType": "message",
    "url": "http://en.tm-ladder.com/{}_rech.php",
    "urlMain": "http://en.tm-ladder.com/index.php",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis"
```

### plug.dj
As of 2021-12-02, plug.dj is returning false positives because the service is down.

```
  "plug.dj": {
    "errorType": "status_code",
    "url": "https://plug.dj/@/{}",
    "urlMain": "https://plug.dj/",
    "username_claimed": "plug-dj-rock",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

## Facenama

As of 2022-02-6, Facenama seems to be down their rebuilding their site
```
  "Facenama": {
    "errorType": "response_url",
    "errorUrl": "https://facenama.com/404.html",
    "regexCheck": "^[-a-zA-Z0-9_]+$",
    "url": "https://facenama.com/{}",
    "urlMain": "https://facenama.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis77"
  },
```
