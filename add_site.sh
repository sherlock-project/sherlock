#!/bin/bash
#add_site.sh
OKFORMAT="[\e[32mOK\e[0m   ]"
ERRORFORMAT="[\e[38;5;196mERROR\e[0m]"
INFOFORMAT="[\e[38;5;44mINFO\e[0m ]"
QUESTIONFORMAT="[?    ]"
WARNINGFORMAT="[\e[33mWARNING\e[0m]"

READsiteName () {
	read siteName
	if [[ $siteName = "" ]];
		then
			printf "$ERRORFORMAT Please enter a name.\n"
			READsiteName
		else
			if grep -Fqi "[$siteName]" sites.md
				then
					printf "$ERRORFORMAT This site is already in the list. Please choose a different one.\n"
					READsiteName
			fi
	fi
}

READurlMain () {
	read urlMain
	if [[ $urlMain != http?(s)://*.* ]];
		then
			printf "$ERRORFORMAT Please enter a valid URL.\n"
			READurlMain
		else
			if grep -Fqi "$urlMain" sites.md
				then
					printf "$ERRORFORMAT This site is already in the list. Please choose a different one.\n"
					printf "$INFOFORMAT Please enter a name of the site you want to add\n$INFOFORMAT (e.g. \e[1mGoogle\e[0m)\n"
					READsiteName
			fi
	fi
}
READurl () {
	read url
	if [[ $url != http?(s)://*.* ]];
		then
			printf "$ERRORFORMAT Please enter a valid URL.\n"
			READurl
		else
			if [[ $url != *{}* ]];
				then
					printf "$ERRORFORMAT Please enter a URL with the username brackets - {}\n"
					READurl
			fi

	fi
}

READerrorType () {
	read -n 1
	if [[ $REPLY = 1 ]];
		#status_code
		then
			echo
			errorType=status_code
			printf "$INFOFORMAT You've selected 'status_code' as errorType.\n"
	elif [[ $REPLY = 2 ]];
		#message
		then
			echo
			errorType=message
			READmessage
	elif [[ $REPLY = 3 ]];
		#response_url
		then
			echo
			errorType=errorUrl
			READresponse_url
		else
			echo
			printf "$QUESTIONFORMAT Please choose a correct option (1,2,3)\n"
			READerrorType
	fi
}

READmessage () {
	printf "$INFOFORMAT You've selected 'message' as errorType.\n$INFOFORMAT Please enter the error message:\n"
	read errorMsg
	if [[ $errorMsg = "" ]];
		then
			printf "$ERRORFORMAT Error message cannot be blank.\n"
			READmessage
	fi
}

READresponse_url () {
	printf "$INFOFORMAT You've selected 'response_url' as errorType.\n$INFOFORMAT Please enter the response URL:\n"
	read errorUrl
	if [[ $errorUrl != http?(s)://*.* ]];
		then
			printf "$ERRORFORMAT Please enter a valid URL.\n"
			READresponse_url
	fi
}

TESTerrorType () {
	printf "\e[1mERROR TYPE (errorType): \e[4m$errorType\e[24m\e[0m\n"
	if [[ $errorType == message ]];
		then
			printf "\e[1mERROR MESSAGE (errorMsg): \e[4m$errorMsg\e[24m\e[0m\n"
	elif [[ $errorType == errorUrl ]];
		then
			printf "\e[1mERROR URL (errorUrl): \e[4m$errorUrl\e[24m\e[0m\n"
	fi
}

TESTwriteFormat () {
	printf "	\"$siteName\": {"
	echo
	if [[ $errorType == status_code ]];
		then
			printf "		\"errorType\": \"status_code\","
			echo
	elif [[ $errorType == message ]];
		then
			printf "		\"errorMsg\": \"$errorMsg\","
			echo
			printf "		\"errorType\": \"message\","
			echo
	elif [[ $errorType == errorUrl ]];
		then
			printf "		\"errorType\": \"response_url\","
			echo
			printf "		\"errorUrl\": \"$errorUrl\","
			echo
	fi
	printf "		\"url\": \"$url\","
	echo
	printf "		\"urlMain\": \"$urlMain\""
	echo
	printf "	}"
}

WRITEtoDataJson () {
	sed "/{data}
   }
/i thing" test.json
}

#WRITEtoDataJson #this is here just for testing purposes, do not uncomment
printf "$INFOFORMAT add_site.sh - a simple script for adding sites to Sherlock\n"
printf "TODO: Make the script automatically add the created site to data.json\n"
printf "$INFOFORMAT Please enter a name of the site you want to add\n$INFOFORMAT (e.g. \e[1mGoogle\e[0m)\n"
READsiteName

printf "$INFOFORMAT Please enter the main url of the site\n$INFOFORMAT (e.g. \e[1mhttps://google.com/\e[0m)\n"
READurlMain

printf "$INFOFORMAT Please enter the url pointing to user profile\n$INFOFORMAT (where {} is the username, e.g. \e[1mhttps://example.com/user/{}\e[0m)\n"
READurl

echo

printf "$INFOFORMAT Please choose a method to determine a non-existent username:\n"
printf "[1] '\e[1mstatus_code\e[0m' - the most common method. This is the case when page returns an error code (like 404) when trying to visit a non-existent user.\n"
printf "Example: https://invaliduser.itch.io/\n\n"
printf "[2] '\e[1mmessage\e[0m' - this works when '\e[1mstatus_code\e[0m' doesn't. It defines a unique string, that is present on a website when trying to visit a non-existent user.\n"
printf "Example: https://www.buzzfeed.com/invalidurl - the error message here is '\e[1mWe can't find the page you're looking for.\e[0m'\n\n"
printf "[3] '\e[1mresponse_url\e[0m' - this is the least used method. It defines a URL, which is a redirect, when trying to visit a non-existent user.\n"
printf "Example: https://pastebin.com/u/invalidurl - when you visit this link, it will redirect you to https://pastebin.com/index\nSo in this case, the 'errorUrl' is \e[1mhttps://pastebin.com/index\e[0m\n"
READerrorType

printf "$INFOFORMAT Please verify the site details you entered:\n"
printf "\e[1mNAME: \e[4m$siteName\e[24m\nMAIN URL (urlMain): \e[4m$urlMain\e[24m\nPROFILE URL (url): \e[4m$url\e[24m\e[0m\n"
TESTerrorType
printf "Do you want to add a site with these informations? Y/N\n"
read -n 1
if [[ $REPLY =~ ^[Yy]$ ]];
	then 
		echo
	else
		exit
fi
printf "$OKFORMAT Copy the following to data.json:\n"
printf "____________________________________________________________\n\n"
TESTwriteFormat
printf "\n____________________________________________________________"
printf "\n\n$WARNINGFORMAT Don't forget to run 'python site_list.py' after modifying data.json, to add $siteName in SITES.md so you can make a proper pull request.\n"
printf "$OKFORMAT Script finished succesfully.\n"