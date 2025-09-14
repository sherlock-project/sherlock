# List Of Sites Removed From Sherlock

This is a list of sites implemented in such a way that the current design of
Sherlock is not capable of determining if a given username exists or not.
They are listed here in the hope that things may change in the future
so they may be re-included.


## gpodder.net

As of 2020-05-25, all usernames are reported as available.

The server is returning a HTTP Status 500 (Internal server error)
for all queries.

```json
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

```json
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

```json
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


```json
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

## Canva

As of 2020-02-23, all usernames are reported as not existing.

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
  "PowerShell Gallery": {
    "errorType": "status_code",
    "rank": 163562,
    "url": "https://www.powershellgallery.com/profiles/{}",
    "urlMain": "https://www.powershellgallery.com",
    "username_claimed": "powershellteam",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## StreamMe

On 2019-04-07, I get a Timed Out message from the website.  It has not
been working earlier either (for some weeks).  It takes about 21s before
the site finally times out, so it really makes getting the results from
Sherlock a pain.

If the site becomes available in the future, we can put it back in.

```json
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

```json
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

```json
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

```json
  "Google Plus": {
    "errorType": "status_code",
    "rank": 1,
    "url": "https://plus.google.com/+{}",
    "urlMain": "https://plus.google.com/",
    "username_claimed": "davidbrin1",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```


## InsaneJournal

As of 2020-02-23, InsaneJournal returns false positive, when providing a username which contains a period.
Since we were not able to find the criteria for a valid username, the best thing to do now is to remove it.

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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
```json
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
I have tried to find out what Coderwall's criteria is for a valid username, but unfortunately I have not been able to
find it and because of this, the best thing we can do now is to remove it.
```json
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
```json
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
```json
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
```json
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
```json
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
As of 2020-08-11, YandexCollection presents us with a recaptcha which prevents us from checking for usernames
```json
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
```json
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
```json
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
```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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

```json
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
```json
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

```json
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
```json
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

```json
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
```json
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

```json
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

```json
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
```json
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
```json
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
```json
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
```json
  "Travellerspoint": {
    "errorMsg": "Wooops. Sorry!",
    "errorType": "message",
    "url": "https://www.travellerspoint.com/users/{}",
    "urlMain": "https://www.travellerspoint.com",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## GDProfiles

As of 2021-06-27, GDProfiles takes way too long to respond. Must be an issue on their side.
```json
  "GDProfiles": {
    "errorType": "status_code",
    "url": "https://gdprofiles.com/{}",
    "urlMain": "https://gdprofiles.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis"
  },
```

## AllTrails

As of 2021-06-27, AllTrails has a captcha which prevents us from checking for usernames on the site.
```json
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

```json
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

```json
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

As of 2021-06-27, NameMC uses captcha through CloudFlare which prevents us from checking if usernames exists on the site.

```json
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

As of 2021-06-27, Steam uses captcha through CloudFlare which prevents us from checking if usernames exists on the site.
```json
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
```json
  "TripAdvisor": {
    "errorMsg": "This page is on vacation\u2026",
    "errorType": "message",
    "url": "https://tripadvisor.com/members/{}",
    "urlMain": "https://tripadvisor.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },

```

### House Mixes

As of 2021-09-04, House Mixes has issues connecting causing Sherlock to freeze.
```json
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
```json
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
```json
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
```json
  "Cloob": {
    "errorType": "status_code",
    "url": "https://www.cloob.com/name/{}",
    "urlMain": "https://www.cloob.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

### TM-Ladder
As of 2021-11-30, TM-Ladder is returning false positives due to rate limits.

```json
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

```json
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
```json
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


## Designspiration

As of 2022-04-17, Designspiration seems to be down or very laggy. Therefore, we're removing the site for now.

```json
  "Designspiration": {
    "errorType": "status_code",
    "url": "https://www.designspiration.net/{}/",
    "urlMain": "https://www.designspiration.net/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## CapFriendly

As of 2022-05-01, CapFriendly always shows that a username exists even though it doesn't. This
then of course causes false positives in Sherlock's results.

```json
  "CapFriendly": {
    "errorMsg": "<div class=\"err show p5\">No results found</div>",
    "errorType": "message",
    "regexCheck": "^[a-zA-z][a-zA-Z0-9_]{2,79}$",
    "url": "https://www.capfriendly.com/users/{}",
    "urlMain": "https://www.capfriendly.com/",
    "username_claimed": "thisactuallyexists",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Gab

As of 2022-05-01, Gab returns false positives because they now use CloudFlare
```json
  "Gab": {
    "errorMsg": "The page you are looking for isn't here.",
    "errorType": "message",
    "url": "https://gab.com/{}",
    "urlMain": "https://gab.com",
    "username_claimed": "a",
    "username_unclaimed": "noonewouldeverusethis"
  },
```

## FanCentro

As of 2022-05-1, FanCentro returns false positives. Will later in new version of Sherlock.

```json
  "FanCentro": {
    "errorMsg": "var environment",
    "errorType": "message",
    "url": "https://fancentro.com/{}",
    "urlMain": "https://fancentro.com/",
    "username_claimed": "nielsrosanna",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Smashcast
As og 2022-05-01, Smashcast is down
```json
  "Smashcast": {
    "errorType": "status_code",
    "url": "https://www.smashcast.tv/api/media/live/{}",
    "urlMain": "https://www.smashcast.tv/",
    "username_claimed": "hello",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Countable

As og 2022-05-01, Countable returns false positives
```json
  "Countable": {
    "errorType": "status_code",
    "url": "https://www.countable.us/{}",
    "urlMain": "https://www.countable.us/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Raidforums

Raidforums is [now run by the FBI](https://twitter.com/janomine/status/1499453777648234501?s=21)
```json
  "Raidforums": {
    "errorType": "status_code",
    "url": "https://raidforums.com/User-{}",
    "urlMain": "https://raidforums.com/",
    "username_claimed": "red",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Pinterest
Removed due to false positive

```json
  "Pinterest": {
    "errorType": "status_code",
    "url": "https://www.pinterest.com/{}/",
    "urlMain": "https://www.pinterest.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis76543"
  }
```

## PCPartPicker
As of 17-07-2022, PCPartPicker requires us to login in order to check if a user exits

```json
  "PCPartPicker": {
    "errorType": "status_code",
    "url": "https://pcpartpicker.com/user/{}",
    "urlMain": "https://pcpartpicker.com",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Ebay
As of 17-07-2022, Ebay is very slow to respond. It was also reported that it returned false positives. So this is something that has been investigated further later.

```json
  "eBay.com": {
    "errorMsg": "The User ID you entered was not found. Please check the User ID and try again.",
    "errorType": "message",
    "url": "https://www.ebay.com/usr/{}",
    "urlMain": "https://www.ebay.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
  "eBay.de": {
    "errorMsg": "Der eingegebene Nutzername wurde nicht gefunden. Bitte pr\u00fcfen Sie den Nutzernamen und versuchen Sie es erneut.",
    "errorType": "message",
    "url": "https://www.ebay.de/usr/{}",
    "urlMain": "https://www.ebay.de/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Ghost
As of 17-07-2022, Ghost returns false positives

```json
  "Ghost": {
    "errorMsg": "Domain Error",
    "errorType": "message",
    "url": "https://{}.ghost.io/",
    "urlMain": "https://ghost.org/",
    "username_claimed": "troyhunt",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

## Atom Discussions
As of 25-07-2022, Atom Discussions seems to not work beceause it keeps on
redirecting to github discussion tab which does not exist and is not specific to a username

```json
  "Atom Discussions": {
    "errorMsg": "Oops! That page doesn\u2019t exist or is private.",
    "errorType": "message",
    "url": "https://discuss.atom.io/u/{}/summary",
    "urlMain": "https://discuss.atom.io",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis"
  }
```

## Gam1ng
As of 25-07-2022, Gam1ng has been permanently moved and is no longer functional

```json
  "Gam1ng": {
    "errorType": "status_code",
    "url": "https://gam1ng.com.br/user/{}",
    "urlMain": "https://gam1ng.com.br",
    "username_claimed": "PinKgirl",
    "username_unclaimed": "noonewouldeverusethis77777"
  }
```

## OGUsers
As of 25-07-2022, OGUsers is now no longer functional

```json
  "OGUsers": {
    "errorType": "status_code",
    "url": "https://ogusers.com/{}",
    "urlMain": "https://ogusers.com/",
    "username_claimed": "ogusers",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

## Otzovik
As of 25-07-2022, Otzovik is now no longer functional

```json
  "Otzovik": {
    "errorType": "status_code",
    "url": "https://otzovik.com/profile/{}",
    "urlMain": "https://otzovik.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

## radio_echo_msk
As of 25-07-2022, radio_echo_msk is now no longer functional

```json
  "radio_echo_msk": {
    "errorType": "status_code",
    "url": "https://echo.msk.ru/users/{}",
    "urlMain": "https://echo.msk.ru/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```
## Ello
As of 06.09.2022, Ello is now behind CloudFlare
```json
  "Ello": {
    "errorMsg": "We couldn't find the page you're looking for",
    "errorType": "message",
    "url": "https://ello.co/{}",
    "urlMain": "https://ello.co/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  }
```

## GitHub Support Community
As of 06.09.2022, GitHub Support Community's endpoint just redirects to the main community page
```json
  "GitHub Support Community": {
    "errorMsg": "Oops! That page doesn\u2019t exist or is private.",
    "errorType": "message",
    "url": "https://github.community/u/{}/summary",
    "urlMain": "https://github.community",
    "username_claimed": "jperl",
    "username_unclaimed": "noonewouldusethis298"
  }
```

## GuruShots
As of 08.09.2022, GuruShots returns false positives because it just returns a blank page. Need to look further into it so that it can be added back.

```json
  "GuruShots": {
    "errorType": "status_code",
    "url": "https://gurushots.com/{}/photos",
    "urlMain": "https://gurushots.com/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Google Developer
As of 09.10.2022, Google Developer returns false positives. The site is dynamic so we're not abl to get any proper results

```json
  "Google Developer": {
    "errorMsg": "Sorry, the profile was not found.",
    "errorType": "message",
    "url": "https://g.dev/{}",
    "urlMain": "https://g.dev/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## mastodon.technology
As of 18.12.2022, mastodon.technology has no A/AAAA records and the [website was shut down by the owner](https://ashfurrow.com/blog/mastodon-technology-shutdown/).

```json
  "mastodon.technology": {
    "errorType": "status_code",
    "url": "https://mastodon.technology/@{}",
    "urlMain": "https://mastodon.xyz/",
    "username_claimed": "ashfurrow",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```


## Aruino
As of 04.02.2023, Arduino returns false positives. Finding a fix is doable but takes some time. Will be fixed later

```json
"Arduino": {
    "errorMsg":"<title>Arduino Cloud</title>",
    "errorType": "message",
    "regexCheck": "^(?![_-])[A-Za-z0-9_-]{3,}$",
    "url": "https://projecthub.arduino.cc/{}",
    "urlMain": "https://www.arduino.cc/",
    "username_claimed": "blue",
    "username_unclaimed": "noonewould"
  },

```

## Zoomit
As of 04.02.2023, Zoomit return false positves. An attempt at finding a fix was made but a lot of time was used without luck. Therefore, it wont be prioritized at the moment.
```json
  "zoomit": {
    "errorMsg": "\u0645\u062a\u0627\u0633\u0641\u0627\u0646\u0647 \u0635\u0641\u062d\u0647 \u06cc\u0627\u0641\u062a \u0646\u0634\u062f",
    "errorType": "message",
    "url": "https://www.zoomit.ir/user/{}",
    "urlMain": "https://www.zoomit.ir",
    "username_claimed": "kossher",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## Facebook
As of 04.02.2023, Facebook returns false positives because we get prompted with the login screen to view the data
```json
"Facebook": {
    "errorType": "status_code",
    "regexCheck": "^[a-zA-Z0-9\\.]{3,49}(?<!\\.com|\\.org|\\.net)$",
    "url": "https://www.facebook.com/{}",
    "urlMain": "https://www.facebook.com/",
    "urlProbe": "https://www.facebook.com/{}/videos/",
    "username_claimed": "hackerman",
    "username_unclaimed": "noonewouldeverusethis7"
  },
```

## BinarySearch
As of 08.02.2023, BinarySearch seems to not be responding at all
```json
  "BinarySearch": {
    "errorMsg": "{}",
    "errorType": "message",
    "regexCheck": "^[a-zA-Z0-9-_]{1,15}$",
    "url": "https://binarysearch.io/@/{}",
    "urlMain": "https://binarysearch.io/",
    "urlProbe": "https://binarysearch.io/api/users/{}/profile",
    "username_claimed": "Eyes_Wide_Shut"
  },
```
## Arduino
As of 15.02.2023, Arduino returns false positives due to some unstable redirects
```json
  "Arduino": {
    "errorType": "status_code",
    "regexCheck": "^(?![_-])[A-Za-z0-9_-]{3,}$",
    "url": "https://create.arduino.cc/projecthub/{}",
    "urlMain": "https://www.arduino.cc/",
    "username_claimed": "blue"
  },
```
## Koo
As of 15.02.2023, Koo returns false positives
```json
  "koo": {
    "errorMsg": "This profile does not exist",
    "errorType": "message",
    "url": "https://www.kooapp.com/profile/{}",
    "urlMain": "https://www.kooapp.com",
    "urlProbe": "https://www.kooapp.com/apiV1/users/handle/{}/valid",
    "username_claimed": "john"
  }
```


## We Heart It
As of  2022.02.25, WeHeartIt no longer allows us to check for usersnames through their website. Visiting their website leads to links to download the mobile application. A potential way of fixing this is to find API endpoints in the app
```json
  "We Heart It": {
    "errorMsg": "Oops! You've landed on a moving target!",
    "errorType": "message",
    "url": "https://weheartit.com/{}",
    "urlMain": "https://weheartit.com/",
    "username_claimed": "ventivogue"
  }
```


## Tinder
As of 2022.03.15, Tinder returns false positives. We will try to rev the API endpoint on the android app to find a better soon

```json
"Tinder": {
    "errorMsg": [
      "<title data-react-helmet=\"true\">Tinder | Dating, Make Friends &amp; Meet New People</title>",
      "<title data-react-helmet=\"true\">Tinder | Match. Chat. Date.</title>"
    ],
    "errorType": "message",
    "url": "https://www.tinder.com/@{}",
    "urlMain": "https://tinder.com/",
    "username_claimed": "blue"
  },
```


## Coil
As of 2023.03.15, Coil has been discontinued. All accounts were deleted and any requests return a 404.

```json
"Coil": {
    "errorMsg": "User not found",
    "errorType": "message",
    "request_method": "POST",
    "request_payload": {
      "operationName": "getCreator",
      "query": "query getCreator($userShortName:String!){getCreator(userShortName:$userShortName){id}}",
      "variables": {
        "userShortName": "{}"
      }
    },
    "url": "https://coil.com/u/{}",
    "urlMain": "https://coil.com/",
    "urlProbe": "https://coil.com/gateway",
    "username_claimed": "adam"
  }
```

## OnlyFans
As of 2023.04.20, OnlyFans returns false negatives on checking usernames with the API endpoint and directly through their website.

```json
"OnlyFans": {
    "errorType": "status_code",
    "isNSFW": true,
    "url": "https://onlyfans.com/{}",
    "urlMain": "https://onlyfans.com/",
    "urlProbe": "https://onlyfans.com/api2/v2/users/{}",
    "username_claimed": "theemilylynne"
  }
```

## OK
As of 2023.04.21, Ok.ru returns false positives
```json
  "OK": {
    "errorType": "status_code",
    "regexCheck": "^[a-zA-Z][a-zA-Z0-9_.-]*$",
    "url": "https://ok.ru/{}",
    "urlMain": "https://ok.ru/",
    "username_claimed": "ok"
  }
```

## ForumhouseRU
As of 2023.04.21, ForumhouseRU returns false positives
```json
  "forumhouseRU": {
    "errorMsg": "\u0423\u043a\u0430\u0437\u0430\u043d\u043d\u044b\u0439 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d. \u041f\u043e\u0436\u0430\u043b\u0443\u0439\u0441\u0442\u0430, \u0432\u0432\u0435\u0434\u0438\u0442\u0435 \u0434\u0440\u0443\u0433\u043e\u0435 \u0438\u043c\u044f.",
    "errorType": "message",
    "url": "https://www.forumhouse.ru/members/?username={}",
    "urlMain": "https://www.forumhouse.ru/",
    "username_claimed": "red"
  }
```

## Enjin
As of 2023.08.29, Enjin has closed down.

```json
"Enjin": {
    "errorMsg": "Yikes, there seems to have been an error. We've taken note and will check out the problem right away!",
    "errorType": "message",
    "url": "https://www.enjin.com/profile/{}",
    "urlMain": "https://www.enjin.com/",
    "username_claimed": "blue"
  },
```

## IRL
As of 2023.08.29, IRL has shut down
```json
  "IRL": {
    "errorType": "status_code",
    "url": "https://www.irl.com/{}",
    "urlMain": "https://www.irl.com/",
    "username_claimed": "hacker"
  }
```

## Munzee
As of 2023.08.29, Munzee requires us to be logged into the site in order to check if a user exists or not
```json
  "Munzee": {
    "errorType": "status_code",
    "url": "https://www.munzee.com/m/{}",
    "urlMain": "https://www.munzee.com/",
    "username_claimed": "blue"
  }
```

## Quizlet
As of 2023.08.29 Quizlet requires us to enable JavaScript to check if a user exsits on the website

```json
"Quizlet": {
    "errorMsg": "Page Unavailable",
    "errorType": "message",
    "url": "https://quizlet.com/{}",
    "urlMain": "https://quizlet.com",
    "username_claimed": "blue"
  }
```

## GunsAndAmmo
As of 2023.08.29, GunsAndAmmo responds with 404 from time to time
```json
  "GunsAndAmmo": {
    "errorType": "status_code",
    "url": "https://forums.gunsandammo.com/profile/{}",
    "urlMain": "https://gunsandammo.com/",
    "username_claimed": "adam"
  }
```

## TikTok
As of 2023.12.21, TikTok returns false positives. This is because the webpage returns a somewhat blank page. This prevents us from being able to check for the existence of usernames. Proxitok does not work either.

```json
  "TikTok": {
    "errorType": "status_code",
    "url": "https://tiktok.com/@{}",
    "urlMain": "https://tiktok.com/",
    "username_claimed": "red"
  },
```

## Lolchess
As of 2023.12.21, Lolchess returns false positives.
```json
  "Lolchess": {
    "errorMsg": "No search results",
    "errorType": "message",
    "url": "https://lolchess.gg/profile/na/{}",
    "urlMain": "https://lolchess.gg/",
    "username_claimed": "blue"
  },
```

## Virgool
As of 2023.12.21, Virgool returns false positives.
```json
  "Virgool": {
    "errorMsg": "\u06f4\u06f0\u06f4",
    "errorType": "message",
    "url": "https://virgool.io/@{}",
    "urlMain": "https://virgool.io/",
    "username_claimed": "blue"
  },
```

## Whonix Forum
As of 2023.12.21, Whonix Forum returns false positives.
```json
  "Whonix Forum": {
    "errorType": "status_code",
    "url": "https://forums.whonix.org/u/{}/summary",
    "urlMain": "https://forums.whonix.org/",
    "username_claimed": "red"
  },
```

## Ebio
As of 2023.12.21, Ebio returns false positives.
```json
  "ebio.gg": {
    "errorType": "status_code",
    "url": "https://ebio.gg/{}",
    "urlMain": "https:/ebio.gg",
    "username_claimed": "dev"
  },
```

## HexRPG
__2024-04-07 :__ HexRPG behind authentication wall. Unable to check usernames without logging in.
```json
  "HexRPG": {
    "errorMsg": "Error : User ",
    "errorType": "message",
    "regexCheck": "^[a-zA-Z0-9_ ]{3,20}$",
    "url": "https://www.hexrpg.com/userinfo/{}",
    "urlMain": "https://www.hexrpg.com/",
    "username_claimed": "blue"
  }
```

## Oracle Communities
__2024-04-07 :__ Oracle Communities behind authentication wall. Unable to check usernames without logging in.
```json
  "Oracle Communities": {
    "errorType": "status_code",
    "url": "https://community.oracle.com/people/{}",
    "urlMain": "https://community.oracle.com",
    "username_claimed": "dev"
  }
```

## Metacritic
__2024-04-07 :__ Non-existent users seemingly displayed as real users with no activity. Needs adjustment.
```json
  "metacritic": {
    "errorMsg": "User not found",
    "errorType": "message",
    "regexCheck": "^(?![-_].)[A-Za-z0-9-_]{3,15}$",
    "url": "https://www.metacritic.com/user/{}",
    "urlMain": "https://www.metacritic.com/",
    "username_claimed": "blue"
  }
```

## G2G
__2024-04-10 :__ Seems to be loading profiles with some wierd javascript setup that sherlock doesn't like, leading to difficult to control false positives
```json
  "G2G": {
    "errorType": "response_url",
    "errorUrl": "https://www.g2g.com/{}",
    "regexCheck": "^[A-Za-z][A-Za-z0-9_]{2,11}$",
    "url": "https://www.g2g.com/{}",
    "urlMain": "https://www.g2g.com/",
    "username_claimed": "user"
  }
```

## Bitcoin Forum
__2024-04-24 :__ BCF seems to have gone defunct. Uncertain.
```json
"BitCoinForum": {
    "errorMsg": "The user whose profile you are trying to view does not exist.",
    "errorType": "message",
    "url": "https://bitcoinforum.com/profile/{}",
    "urlMain": "https://bitcoinforum.com",
    "username_claimed": "bitcoinforum.com"
  }
```

## Zhihu
As of 24.06.2024, Zhihu returns false positives as they obfuscate the code thats returned. Checking for patterns may allow us to find a way to detect the existans of a user, this will be need to be worked on later
```json

  "Zhihu": {
    "errorMsg": "用户不存在",
    "errorType": "message",
    "url": "https://www.zhihu.com/people/{}",
    "urlMain": "https://www.zhihu.com/",
    "username_claimed": "blue"
  }
```

## Penetestit

As of 24.06.2024, Pentestit returns a 403. This is most likely due to a new site structures

```json
  "labpentestit": {
    "errorType": "response_url",
    "errorUrl": "https://lab.pentestit.ru/{}",
    "url": "https://lab.pentestit.ru/profile/{}",
    "urlMain": "https://lab.pentestit.ru/",
    "username_claimed": "CSV"
  }
```


## Euw
__2024-06-09 :__ errorMsg detection doesn't work anymore, because the error message is included in HTTP request body, even in successful search
```json
"Euw": {
    "errorMsg": "This summoner is not registered at OP.GG. Please check spelling.",
    "errorType": "message",
    "url": "https://euw.op.gg/summoner/userName={}",
    "urlMain": "https://euw.op.gg/",
    "username_claimed": "blue"
  }
```

## Etsy
__2024-06-10 :__ Http request returns 403 forbidden, and tries to verify the connection, so it doesn't work anymore
```json
"Etsy": {
    "errorType": "status_code",
    "url": "https://www.etsy.com/shop/{}",
    "urlMain": "https://www.etsy.com/",
    "username_claimed": "JennyKrafts"
  }
```

## Alik.cz
__2024-07-21 :__ Target is now BLACKLISTED from the default manifest due to the site recieving unnecessarily high traffic from Sherlock (by request of the site owners). This target is not permitted to be reactivited. Inclusion in unrelated manifests is not impacted, but it is discouraged.

## 8tracks
__2025-02-02 :__ Might be dead again. Nobody knows for sure.
```json
"8tracks": {
    "errorType": "message",
    "errorMsg": "\"available\":true",
    "headers": {
      "Accept-Language": "en-US,en;q=0.5"
    },
    "url": "https://8tracks.com/{}",
    "urlProbe": "https://8tracks.com/users/check_username?login={}&format=jsonh",
    "urlMain": "https://8tracks.com/",
    "username_claimed": "blue"
  }
```

## Shpock
__2025-02-02 :__ Can likely be added back with a new endpoint (source username availability endpoint from mobile app reg flow?)
```json
"Shpock": {
    "errorType": "status_code",
    "url": "https://www.shpock.com/shop/{}/items",
    "urlMain": "https://www.shpock.com/",
    "username_claimed": "user"
  }
```

## Twitch
__2025-02-02 :__
```json
"Twitch": {
    "errorType": "message",
    "errorMsg": "components.availability-tracking.warn-unavailable.component",
    "url": "https://www.twitch.tv/{}",
    "urlMain": "https://www.twitch.tv/",
    "urlProbe": "https://m.twitch.tv/{}",
    "username_claimed": "jenny"
  }
```

## Fiverr
__2025-02-02 :__ Fiverr added CSRF protections that messed with this test
```json
"Fiverr": {
    "errorMsg": "\"status\":\"success\"",
    "errorType": "message",
    "headers": {
      "Content-Type": "application/json",
      "Accept-Language": "en-US,en;q=0.9"
    },
    "regexCheck": "^[A-Za-z][A-Za-z\\d_]{5,14}$",
    "request_method": "POST",
    "request_payload": {
      "username": "{}"
    },
    "url": "https://www.fiverr.com/{}",
    "urlMain": "https://www.fiverr.com/",
    "urlProbe": "https://www.fiverr.com/validate_username",
    "username_claimed": "blueman"
  }
```

## BabyRU
__2025-02-02 :__ Just being problematic (possibly related to errorMsg encoding?)
```json
"babyRU": {
    "errorMsg": [
      "\u0421\u0442\u0440\u0430\u043d\u0438\u0446\u0430, \u043a\u043e\u0442\u043e\u0440\u0443\u044e \u0432\u044b \u0438\u0441\u043a\u0430\u043b\u0438, \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430",
      "Доступ с вашего IP-адреса временно ограничен"
    ],
    "errorType": "message",
    "url": "https://www.baby.ru/u/{}/",
    "urlMain": "https://www.baby.ru/",
    "username_claimed": "blue"
  }
```

## v0.dev
__2025-02-16 :__ Unsure if any way to view profiles exists now
```json
"v0.dev": {
    "errorType": "message",
    "errorMsg": "<title>v0 by Vercel</title>",
    "url": "https://v0.dev/{}",
    "urlMain": "https://v0.dev",
    "username_claimed": "t3dotgg"
  }
```

## TorrentGalaxy
__2025-07-06 :__ Site appears to have gone offline in March and hasn't come back
```json
  "TorrentGalaxy": {
    "errorMsg": "<title>TGx:Can't show details</title>",
    "errorType": "message",
    "regexCheck": "^[A-Za-z0-9]{3,15}$",
    "url": "https://torrentgalaxy.to/profile/{}",
    "urlMain": "https://torrentgalaxy.to/",
    "username_claimed": "GalaxyRG"
  },
```
