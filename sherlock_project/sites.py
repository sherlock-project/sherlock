"""Sherlock Sites Information Module

This module supports storing information about websites.
This is the raw data that will be used to search for usernames.
"""
import json
import requests
import secrets

class SiteInformation:
    def __init__(self, name, url_home, url_username_format, username_claimed,
                information, is_nsfw, username_unclaimed=secrets.token_urlsafe(10)):
        """Create Site Information Object.

        Contains information about a specific website.

        Keyword Arguments:
        self                   -- This object.
        name                   -- String which identifies site.
        url_home               -- String containing URL for home of site.
        url_username_format    -- String containing URL for Username format
                                  on site.
                                  NOTE:  The string should contain the
                                         token "{}" where the username should
                                         be substituted.  For example, a string
                                         of "https://somesite.com/users/{}"
                                         indicates that the individual
                                         usernames would show up under the
                                         "https://somesite.com/users/" area of
                                         the website.
        username_claimed       -- String containing username which is known
                                  to be claimed on website.
        username_unclaimed     -- String containing username which is known
                                  to be unclaimed on website.
        information            -- Dictionary containing all known information
                                  about website.
                                  NOTE:  Custom information about how to
                                         actually detect the existence of the
                                         username will be included in this
                                         dictionary.  This information will
                                         be needed by the detection method,
                                         but it is only recorded in this
                                         object for future use.
        is_nsfw                -- Boolean indicating if site is Not Safe For Work.

        Return Value:
        Nothing.
        """

        self.name = name
        self.url_home = url_home
        self.url_username_format = url_username_format

        self.username_claimed = username_claimed
        self.username_unclaimed = secrets.token_urlsafe(32)
        self.information = information
        self.is_nsfw  = is_nsfw

        return

    def __str__(self):
        """Convert Object To String.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nicely formatted string to get information about this object.
        """
        
        return f"{self.name} ({self.url_home})"


class SitesInformation:
    def __init__(self, data_file_path=None):
        """Create Sites Information Object.

        Contains information about all supported websites.

        Keyword Arguments:
        self                   -- This object.
        data_file_path         -- String which indicates path to data file.
                                  The file name must end in ".json".

                                  There are 3 possible formats:
                                   * Absolute File Format
                                     For example, "c:/stuff/data.json".
                                   * Relative File Format
                                     The current working directory is used
                                     as the context.
                                     For example, "data.json".
                                   * URL Format
                                     For example,
                                     "https://example.com/data.json", or
                                     "http://example.com/data.json".

                                  An exception will be thrown if the path
                                  to the data file is not in the expected
                                  format, or if there was any problem loading
                                  the file.

                                  If this option is not specified, then a
                                  default site list will be used.

        Return Value:
        Nothing.
        """

        if not data_file_path:
            # The default data file is the live data.json which is in the GitHub repo. The reason why we are using
            # this instead of the local one is so that the user has the most up-to-date data. This prevents
            # users from creating issue about false positives which has already been fixed or having outdated data
            data_file_path = "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock_project/resources/data.json"

        # Ensure that specified data file has correct extension.
        if not data_file_path.lower().endswith(".json"):
            raise FileNotFoundError(f"Incorrect JSON file extension for data file '{data_file_path}'.")

        # if "http://"  == data_file_path[:7].lower() or "https://" == data_file_path[:8].lower():
        if data_file_path.lower().startswith("http"):
            # Reference is to a URL.
            try:
                response = requests.get(url=data_file_path)
            except Exception as error:
                raise FileNotFoundError(
                    f"Problem while attempting to access data file URL '{data_file_path}':  {error}"
                )

            if response.status_code != 200:
                raise FileNotFoundError(f"Bad response while accessing "
                                        f"data file URL '{data_file_path}'."
                                        )
            try:
                site_data = response.json()
            except Exception as error:
                raise ValueError(
                    f"Problem parsing json contents at '{data_file_path}':  {error}."
                )

        else:
            # Reference is to a file.
            try:
                with open(data_file_path, "r", encoding="utf-8") as file:
                    try:
                        site_data = json.load(file)
                    except Exception as error:
                        raise ValueError(
                            f"Problem parsing json contents at '{data_file_path}':  {error}."
                        )

            except FileNotFoundError:
                raise FileNotFoundError(f"Problem while attempting to access "
                                        f"data file '{data_file_path}'."
                                        )
        
        site_data.pop('$schema', None)

        self.sites = {}

        # Add all site information from the json file to internal site list.
        for site_name in site_data:
            try:

                self.sites[site_name] = \
                    SiteInformation(site_name,
                                    site_data[site_name]["urlMain"],
                                    site_data[site_name]["url"],
                                    site_data[site_name]["username_claimed"],
                                    site_data[site_name],
                                    site_data[site_name].get("isNSFW",False)

                                    )
            except KeyError as error:
                raise ValueError(
                    f"Problem parsing json contents at '{data_file_path}':  Missing attribute {error}."
                )
            except TypeError:
                print(f"Encountered TypeError parsing json contents for target '{site_name}' at {data_file_path}\nSkipping target.\n")

        return

    def remove_nsfw_sites(self, do_not_remove: list = []):
        """
        Remove NSFW sites from the sites, if isNSFW flag is true for site

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        None
        """
        sites = {}
        do_not_remove = [site.casefold() for site in do_not_remove]
        for site in self.sites:
            if self.sites[site].is_nsfw and site.casefold() not in do_not_remove:
                continue
            sites[site] = self.sites[site]  
        self.sites =  sites

    def site_name_list(self):
        """Get Site Name List.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        List of strings containing names of sites.
        """

        return sorted([site.name for site in self], key=str.lower)

    def __iter__(self):
        """Iterator For Object.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Iterator for sites object.
        """

        for site_name in self.sites:
            yield self.sites[site_name]

    def __len__(self):
        """Length For Object.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Length of sites object.
        """
        ---
title: 'List of supported sites'
sidebarTitle: 'Supported sites'
icon: 'globe'
description: 'Sherlock currently supports **400+** sites'
---
1. [1337x](https://www.1337x.to/) 
1. [2Dimensions](https://2Dimensions.com/) 
1. [7Cups](https://www.7cups.com/) 
1. [9GAG](https://www.9gag.com/) 
1. [APClips](https://apclips.com/) **(NSFW)**
1. [About.me](https://about.me/) 
1. [Academia.edu](https://www.academia.edu/) 
1. [AdmireMe.Vip](https://admireme.vip/) **(NSFW)**
1. [Airbit](https://airbit.com/) 
1. [Airliners](https://www.airliners.net/) 
1. [All Things Worn](https://www.allthingsworn.com) **(NSFW)**
1. [AllMyLinks](https://allmylinks.com/) 
1. [AniWorld](https://aniworld.to/) 
1. [Anilist](https://anilist.co/) 
1. [Apple Developer](https://developer.apple.com) 
1. [Apple Discussions](https://discussions.apple.com) 
1. [Archive of Our Own](https://archiveofourown.org/) 
1. [Archive.org](https://archive.org) 
1. [ArtStation](https://www.artstation.com/) 
1. [Asciinema](https://asciinema.org) 
1. [Ask Fedora](https://ask.fedoraproject.org/) 
1. [Atcoder](https://atcoder.jp/) 
1. [Audiojungle](https://audiojungle.net/) 
1. [Autofrage](https://www.autofrage.net/) 
1. [Avizo](https://www.avizo.cz/) 
1. [BOOTH](https://booth.pm/) 
1. [Bandcamp](https://www.bandcamp.com/) 
1. [Bazar.cz](https://www.bazar.cz/) 
1. [Behance](https://www.behance.net/) 
1. [Bezuzyteczna](https://bezuzyteczna.pl) 
1. [BiggerPockets](https://www.biggerpockets.com/) 
1. [BioHacking](https://forum.dangerousthings.com/) 
1. [BitBucket](https://bitbucket.org/) 
1. [Bitwarden Forum](https://bitwarden.com/) 
1. [Blipfoto](https://www.blipfoto.com/) 
1. [Blogger](https://www.blogger.com/) 
1. [Bluesky](https://bsky.app/) 
1. [BoardGameGeek](https://boardgamegeek.com) 
1. [BongaCams](https://pt.bongacams.com) **(NSFW)**
1. [Bookcrossing](https://www.bookcrossing.com/) 
1. [BraveCommunity](https://community.brave.com/) 
1. [BugCrowd](https://bugcrowd.com/) 
1. [BuyMeACoffee](https://www.buymeacoffee.com/) 
1. [BuzzFeed](https://buzzfeed.com/) 
1. [CGTrader](https://www.cgtrader.com) 
1. [CNET](https://www.cnet.com/) 
1. [CSSBattle](https://cssbattle.dev) 
1. [CTAN](https://ctan.org/) 
1. [Caddy Community](https://caddy.community/) 
1. [Car Talk Community](https://community.cartalk.com/) 
1. [Carbonmade](https://carbonmade.com/) 
1. [Career.habr](https://career.habr.com/) 
1. [Championat](https://www.championat.com/) 
1. [Chaos](https://chaos.social/) 
1. [Chatujme.cz](https://chatujme.cz/) 
1. [ChaturBate](https://chaturbate.com) **(NSFW)**
1. [Chess](https://www.chess.com/) 
1. [Choice Community](https://choice.community/) 
1. [Clapper](https://clapperapp.com/) 
1. [CloudflareCommunity](https://community.cloudflare.com/) 
1. [Clozemaster](https://www.clozemaster.com) 
1. [Clubhouse](https://www.clubhouse.com) 
1. [Code Snippet Wiki](https://codesnippets.fandom.com) 
1. [Codeberg](https://codeberg.org/) 
1. [Codecademy](https://www.codecademy.com/) 
1. [Codechef](https://www.codechef.com/) 
1. [Codeforces](https://codeforces.com/) 
1. [Codepen](https://codepen.io/) 
1. [Coders Rank](https://codersrank.io/) 
1. [Coderwall](https://coderwall.com) 
1. [Codewars](https://www.codewars.com) 
1. [Coinvote](https://coinvote.cc/) 
1. [ColourLovers](https://www.colourlovers.com/) 
1. [Contently](https://contently.com/) 
1. [Coroflot](https://coroflot.com/) 
1. [Cracked](https://www.cracked.com/) 
1. [Crevado](https://crevado.com/) 
1. [Crowdin](https://crowdin.com/) 
1. [Cryptomator Forum](https://community.cryptomator.org/) 
1. [Cults3D](https://cults3d.com/en) 
1. [CyberDefenders](https://cyberdefenders.org/) 
1. [DEV Community](https://dev.to/) 
1. [DMOJ](https://dmoj.ca/) 
1. [DailyMotion](https://www.dailymotion.com/) 
1. [Dealabs](https://www.dealabs.com/) 
1. [DeviantART](https://deviantart.com) 
1. [DigitalSpy](https://forums.digitalspy.com/) 
1. [Discogs](https://www.discogs.com/) 
1. [Discord](https://discord.com/) 
1. [Discuss.Elastic.co](https://discuss.elastic.co/) 
1. [Disqus](https://disqus.com/) 
1. [Docker Hub](https://hub.docker.com/) 
1. [Dribbble](https://dribbble.com/) 
1. [Duolingo](https://duolingo.com/) 
1. [Eintracht Frankfurt Forum](https://community.eintracht.de/) 
1. [Empretienda AR](https://empretienda.com) 
1. [Envato Forum](https://forums.envato.com/) 
1. [Erome](https://www.erome.com/) **(NSFW)**
1. [Exposure](https://exposure.co/) 
1. [EyeEm](https://www.eyeem.com/) 
1. [F3.cool](https://f3.cool/) 
1. [Fameswap](https://fameswap.com/) 
1. [Fandom](https://www.fandom.com/) 
1. [Fanpop](https://www.fanpop.com/) 
1. [Finanzfrage](https://www.finanzfrage.net/) 
1. [Flickr](https://www.flickr.com/) 
1. [Flightradar24](https://www.flightradar24.com/) 
1. [Flipboard](https://flipboard.com/) 
1. [Football](https://www.rusfootball.info/) 
1. [FortniteTracker](https://fortnitetracker.com/challenges) 
1. [Forum Ophilia](https://www.forumophilia.com/) **(NSFW)**
1. [Fosstodon](https://fosstodon.org/) 
1. [Freelance.habr](https://freelance.habr.com/) 
1. [Freelancer](https://www.freelancer.com/) 
1. [Freesound](https://freesound.org/) 
1. [GNOME VCS](https://gitlab.gnome.org/) 
1. [GaiaOnline](https://www.gaiaonline.com/) 
1. [Gamespot](https://www.gamespot.com/) 
1. [GeeksforGeeks](https://www.geeksforgeeks.org/) 
1. [Genius (Artists)](https://genius.com/) 
1. [Genius (Users)](https://genius.com/) 
1. [Gesundheitsfrage](https://www.gesundheitsfrage.net/) 
1. [GetMyUni](https://getmyuni.com/) 
1. [Giant Bomb](https://www.giantbomb.com/) 
1. [Giphy](https://giphy.com/) 
1. [GitBook](https://gitbook.com/) 
1. [GitHub](https://www.github.com/) 
1. [GitLab](https://gitlab.com/) 
1. [Gitea](https://gitea.com/) 
1. [Gitee](https://gitee.com/) 
1. [GoodReads](https://www.goodreads.com/) 
1. [Google Play](https://play.google.com) 
1. [Gradle](https://gradle.org/) 
1. [Grailed](https://www.grailed.com/) 
1. [Gravatar](http://en.gravatar.com/) 
1. [Gumroad](https://www.gumroad.com/) 
1. [Gutefrage](https://www.gutefrage.net/) 
1. [HackTheBox](https://forum.hackthebox.com/) 
1. [Hackaday](https://hackaday.io/) 
1. [HackenProof (Hackers)](https://hackenproof.com/) 
1. [HackerEarth](https://hackerearth.com/) 
1. [HackerNews](https://news.ycombinator.com/) 
1. [HackerOne](https://hackerone.com/) 
1. [HackerRank](https://hackerrank.com/) 
1. [Harvard Scholar](https://scholar.harvard.edu/) 
1. [Hashnode](https://hashnode.com) 
1. [Heavy-R](https://www.heavy-r.com/) **(NSFW)**
1. [Holopin](https://holopin.io) 
1. [Houzz](https://houzz.com/) 
1. [HubPages](https://hubpages.com/) 
1. [Hubski](https://hubski.com/) 
1. [HudsonRock](https://hudsonrock.com) 
1. [Hugging Face](https://huggingface.co/) 
1. [IFTTT](https://www.ifttt.com/) 
1. [IRC-Galleria](https://irc-galleria.net/) 
1. [Icons8 Community](https://community.icons8.com/) 
1. [Image Fap](https://www.imagefap.com/) **(NSFW)**
1. [ImgUp.cz](https://imgup.cz/) 
1. [Imgur](https://imgur.com/) 
1. [Instagram](https://instagram.com/) 
1. [Instructables](https://www.instructables.com/) 
1. [Intigriti](https://app.intigriti.com) 
1. [Ionic Forum](https://forum.ionicframework.com/) 
1. [Issuu](https://issuu.com/) 
1. [Itch.io](https://itch.io/) 
1. [Itemfix](https://www.itemfix.com/) 
1. [Jellyfin Weblate](https://translate.jellyfin.org/) 
1. [Jimdo](https://jimdosite.com/) 
1. [Joplin Forum](https://discourse.joplinapp.org/) 
1. [Kaggle](https://www.kaggle.com/) 
1. [Keybase](https://keybase.io/) 
1. [Kick](https://kick.com/) 
1. [Kik](http://kik.me/) 
1. [Kongregate](https://www.kongregate.com/) 
1. [LOR](https://linux.org.ru/) 
1. [Launchpad](https://launchpad.net/) 
1. [LeetCode](https://leetcode.com/) 
1. [LessWrong](https://www.lesswrong.com/) 
1. [Letterboxd](https://letterboxd.com/) 
1. [LibraryThing](https://www.librarything.com/) 
1. [Lichess](https://lichess.org) 
1. [LinkedIn](https://linkedin.com) 
1. [Linktree](https://linktr.ee/) 
1. [Listed](https://listed.to/) 
1. [LiveJournal](https://www.livejournal.com/) 
1. [Lobsters](https://lobste.rs/) 
1. [LottieFiles](https://lottiefiles.com/) 
1. [LushStories](https://www.lushstories.com/) **(NSFW)**
1. [MMORPG Forum](https://forums.mmorpg.com/) 
1. [Medium](https://medium.com/) 
1. [Memrise](https://www.memrise.com/) 
1. [Minecraft](https://minecraft.net/) 
1. [MixCloud](https://www.mixcloud.com/) 
1. [Monkeytype](https://monkeytype.com/) 
1. [Motherless](https://motherless.com/) **(NSFW)**
1. [Motorradfrage](https://www.motorradfrage.net/) 
1. [MyAnimeList](https://myanimelist.net/) 
1. [MyMiniFactory](https://www.myminifactory.com/) 
1. [Mydramalist](https://mydramalist.com) 
1. [Myspace](https://myspace.com/) 
1. [NICommunityForum](https://www.native-instruments.com/forum/) 
1. [NationStates Nation](https://nationstates.net) 
1. [NationStates Region](https://nationstates.net) 
1. [Naver](https://naver.com) 
1. [Needrom](https://www.needrom.com/) 
1. [Newgrounds](https://newgrounds.com) 
1. [Nextcloud Forum](https://nextcloud.com/) 
1. [Nightbot](https://nightbot.tv/) 
1. [Ninja Kiwi](https://ninjakiwi.com/) 
1. [NintendoLife](https://www.nintendolife.com/) 
1. [NitroType](https://www.nitrotype.com/) 
1. [NotABug.org](https://notabug.org/) 
1. [Nyaa.si](https://nyaa.si/) 
1. [OpenStreetMap](https://www.openstreetmap.org/) 
1. [Opensource](https://opensource.com/) 
1. [OurDJTalk](https://ourdjtalk.com/) 
1. [PCGamer](https://pcgamer.com) 
1. [PSNProfiles.com](https://psnprofiles.com/) 
1. [Packagist](https://packagist.org/) 
1. [Pastebin](https://pastebin.com/) 
1. [Patreon](https://www.patreon.com/) 
1. [PentesterLab](https://pentesterlab.com/) 
1. [PepperIT](https://www.pepper.it) 
1. [Periscope](https://www.periscope.tv/) 
1. [Pinkbike](https://www.pinkbike.com/) 
1. [PlayStore](https://play.google.com/store) 
1. [PocketStars](https://pocketstars.com/) **(NSFW)**
1. [Pokemon Showdown](https://pokemonshowdown.com) 
1. [Polarsteps](https://polarsteps.com/) 
1. [Polygon](https://www.polygon.com/) 
1. [Polymart](https://polymart.org/) 
1. [Pornhub](https://pornhub.com/) **(NSFW)**
1. [ProductHunt](https://www.producthunt.com/) 
1. [PromoDJ](http://promodj.com/) 
1. [PyPi](https://pypi.org) 
1. [Rajce.net](https://www.rajce.idnes.cz/) 
1. [Rarible](https://rarible.com/) 
1. [Rate Your Music](https://rateyourmusic.com/) 
1. [Rclone Forum](https://forum.rclone.org/) 
1. [RedTube](https://www.redtube.com/) **(NSFW)**
1. [Redbubble](https://www.redbubble.com/) 
1. [Reddit](https://www.reddit.com/) 
1. [Reisefrage](https://www.reisefrage.net/) 
1. [Replit.com](https://replit.com/) 
1. [ResearchGate](https://www.researchgate.net/) 
1. [ReverbNation](https://www.reverbnation.com/) 
1. [Roblox](https://www.roblox.com/) 
1. [RocketTube](https://www.rockettube.com/) **(NSFW)**
1. [RoyalCams](https://royalcams.com) 
1. [RubyGems](https://rubygems.org/) 
1. [Rumble](https://rumble.com/) 
1. [RuneScape](https://www.runescape.com/) 
1. [SWAPD](https://swapd.co/) 
1. [Sbazar.cz](https://www.sbazar.cz/) 
1. [Scratch](https://scratch.mit.edu/) 
1. [Scribd](https://www.scribd.com/) 
1. [ShitpostBot5000](https://www.shitpostbot.com/) 
1. [Signal](https://community.signalusers.org) 
1. [Sketchfab](https://sketchfab.com/) 
1. [Slack](https://slack.com) 
1. [Slant](https://www.slant.co/) 
1. [Slashdot](https://slashdot.org) 
1. [SlideShare](https://slideshare.net/) 
1. [Slides](https://slides.com/) 
1. [SmugMug](https://smugmug.com) 
1. [Smule](https://www.smule.com/) 
1. [Snapchat](https://www.snapchat.com) 
1. [SoundCloud](https://soundcloud.com/) 
1. [SourceForge](https://sourceforge.net/) 
1. [SoylentNews](https://soylentnews.org) 
1. [Speedrun.com](https://speedrun.com/) 
1. [Spells8](https://spells8.com) 
1. [Splice](https://splice.com/) 
1. [Splits.io](https://splits.io) 
1. [Sporcle](https://www.sporcle.com/) 
1. [Sportlerfrage](https://www.sportlerfrage.net/) 
1. [SportsRU](https://www.sports.ru/) 
1. [Spotify](https://open.spotify.com/) 
1. [Star Citizen](https://robertsspaceindustries.com/) 
1. [Steam Community (Group)](https://steamcommunity.com/) 
1. [Steam Community (User)](https://steamcommunity.com/) 
1. [Strava](https://www.strava.com/) 
1. [SublimeForum](https://forum.sublimetext.com/) 
1. [TETR.IO](https://tetr.io) 
1. [TRAKTRAIN](https://traktrain.com/) 
1. [Telegram](https://t.me/) 
1. [Tellonym.me](https://tellonym.me/) 
1. [Tenor](https://tenor.com/) 
1. [ThemeForest](https://themeforest.net/) 
1. [Tiendanube](https://www.tiendanube.com/) 
1. [TnAFlix](https://www.tnaflix.com/) **(NSFW)**
1. [Topcoder](https://topcoder.com/) 
1. [TorrentGalaxy](https://torrentgalaxy.to/) 
1. [TradingView](https://www.tradingview.com/) 
1. [Trakt](https://www.trakt.tv/) 
1. [TrashboxRU](https://trashbox.ru/) 
1. [Trawelling](https://traewelling.de/) 
1. [Trello](https://trello.com/) 
1. [TryHackMe](https://tryhackme.com/) 
1. [Tuna](https://tuna.voicemod.net/) 
1. [Tweakers](https://tweakers.net) 
1. [Twitter](https://x.com/) 
1. [Typeracer](https://typeracer.com) 
1. [Ultimate-Guitar](https://ultimate-guitar.com/) 
1. [Unsplash](https://unsplash.com/) 
1. [Untappd](https://untappd.com/) 
1. [VK](https://vk.com/) 
1. [VLR](https://www.vlr.gg) 
1. [VSCO](https://vsco.co/) 
1. [Velog](https://velog.io/) 
1. [Velomania](https://forum.velomania.ru/) 
1. [Venmo](https://venmo.com/) 
1. [Vero](https://vero.co/) 
1. [Vimeo](https://vimeo.com/) 
1. [VirusTotal](https://www.virustotal.com/) 
1. [WICG Forum](https://discourse.wicg.io/) 
1. [Warrior Forum](https://www.warriorforum.com/) 
1. [Wattpad](https://www.wattpad.com/) 
1. [WebNode](https://www.webnode.cz/) 
1. [Weblate](https://hosted.weblate.org/) 
1. [Weebly](https://weebly.com/) 
1. [Wikidot](http://www.wikidot.com/) 
1. [Wikipedia](https://www.wikipedia.org/) 
1. [Windy](https://windy.com/) 
1. [Wix](https://wix.com/) 
1. [WolframalphaForum](https://community.wolfram.com/) 
1. [WordPress](https://wordpress.com) 
1. [WordPressOrg](https://wordpress.org/) 
1. [Wordnik](https://www.wordnik.com/) 
1. [Wykop](https://www.wykop.pl) 
1. [Xbox Gamertag](https://xboxgamertag.com/) 
1. [Xvideos](https://xvideos.com/) **(NSFW)**
1. [YandexMusic](https://music.yandex) 
1. [YouNow](https://www.younow.com/) 
1. [YouPic](https://youpic.com/) 
1. [YouPorn](https://youporn.com) **(NSFW)**
1. [YouTube](https://www.youtube.com/) 
1. [akniga](https://akniga.org/profile/blue/) 
1. [authorSTREAM](http://www.authorstream.com/) 
1. [babyblogRU](https://www.babyblog.ru/) 
1. [chaos.social](https://chaos.social/) 
1. [couchsurfing](https://www.couchsurfing.com/) 
1. [d3RU](https://d3.ru/) 
1. [dailykos](https://www.dailykos.com) 
1. [datingRU](http://dating.ru) 
1. [devRant](https://devrant.com/) 
1. [drive2](https://www.drive2.ru/) 
1. [eGPU](https://egpu.io/) 
1. [eintracht](https://eintracht.de) 
1. [exophase](https://www.exophase.com/) 
1. [fixya](https://www.fixya.com) 
1. [fl](https://www.fl.ru/) 
1. [forum_guns](https://forum.guns.ru/) 
1. [freecodecamp](https://www.freecodecamp.org/) 
1. [furaffinity](https://www.furaffinity.net) 
1. [geocaching](https://www.geocaching.com/) 
1. [habr](https://habr.com/) 
1. [hackster](https://www.hackster.io) 
1. [hunting](https://www.hunting.ru/forum/) 
1. [igromania](http://forum.igromania.ru/) 
1. [interpals](https://www.interpals.net/) 
1. [irecommend](https://irecommend.ru/) 
1. [jbzd.com.pl](https://jbzd.com.pl/) 
1. [jeuxvideo](https://www.jeuxvideo.com) 
1. [kaskus](https://www.kaskus.co.id/) 
1. [kofi](https://ko-fi.com) 
1. [kwork](https://www.kwork.ru/) 
1. [last.fm](https://last.fm/) 
1. [leasehackr](https://forum.leasehackr.com/) 
1. [livelib](https://www.livelib.ru/) 
1. [mastodon.cloud](https://mastodon.cloud/) 
1. [mastodon.social](https://chaos.social/) 
1. [mastodon.xyz](https://mastodon.xyz/) 
1. [mercadolivre](https://www.mercadolivre.com.br) 
1. [minds](https://www.minds.com) 
1. [moikrug](https://moikrug.ru/) 
1. [mstdn.io](https://mstdn.io/) 
1. [nairaland.com](https://www.nairaland.com/) 
1. [nnRU](https://www.nn.ru/) 
1. [note](https://note.com/) 
1. [npm](https://www.npmjs.com/) 
1. [omg.lol](https://home.omg.lol) 
1. [opennet](https://www.opennet.ru/) 
1. [osu!](https://osu.ppy.sh/) 
1. [phpRU](https://php.ru/forum/) 
1. [pikabu](https://pikabu.ru/) 
1. [pr0gramm](https://pr0gramm.com/) 
1. [prog.hu](https://prog.hu/) 
1. [satsisRU](https://satsis.info/) 
1. [sessionize](https://sessionize.com/) 
1. [social.tchncs.de](https://social.tchncs.de/) 
1. [spletnik](https://spletnik.ru/) 
1. [svidbook](https://www.svidbook.ru/) 
1. [threads](https://www.threads.net/) 
1. [toster](https://www.toster.ru/) 
1. [uid](https://uid.me/) 
1. [xHamster](https://xhamster.com) **(NSFW)**
1. [znanylekarz.pl](https://znanylekarz.pl
        return len(self.sites)
