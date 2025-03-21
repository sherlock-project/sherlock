# Sherlock Actor on Apify

[![Sherlock Actor](https://apify.com/actor-badge?actor=netmilk/sherlock)](https://apify.com/netmilk/sherlock?fpr=sherlock)

This Actor wraps the [Sherlock Project](https://sherlockproject.xyz/) to provide serverless username reconnaissance across social networks in the cloud. It helps you find usernames across multiple social media platforms without installing and running the tool locally.

## What are Actors?
[Actors](https://docs.apify.com/platform/actors?fpr=sherlock) are serverless microservices running on the [Apify Platform](https://apify.com/?fpr=sherlock). They are based on the [Actor SDK](https://docs.apify.com/sdk/js?fpr=sherlock) and can be found in the [Apify Store](https://apify.com/store?fpr=sherlock). Learn more about Actors in the [Apify Whitepaper](https://whitepaper.actor?fpr=sherlock).

## Usage

### Apify Console

1. Go to the Apify Actor page
2. Click "Run"
3. In the input form, fill in **Username(s)** to search for
4. The Actor will run and produce its outputs in the default datastore


### Apify CLI

```bash
apify call YOUR_USERNAME/sherlock --input='{
  "usernames": ["johndoe", "janedoe"]
}'
```

### Using Apify API

```bash
curl --request POST \
  --url "https://api.apify.com/v2/acts/YOUR_USERNAME~sherlock/run" \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer YOUR_API_TOKEN' \
  --data '{
  "usernames": ["johndoe", "janedoe"],
  }
}'
```

## Input Parameters

The Actor accepts a JSON schema with the following structure:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `usernames` | array | Yes | - | List of usernames to search for |
| `usernames[]` | string | Yes | "json" | Username to search for |


### Example Input

```json
{
  "usernames": ["techuser", "designuser"],
}
```

## Output

The Actor provides three types of outputs:

### Dataset Record*

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | Yes | Username the search was conducted for |
| `links` | arrray | Yes | Array with found links to the social media |
| `links[]`| string | No | URL to the account

### Example Dataset Item (JSON)

```json
{
  "username": "johndoe",
  "links": [
    "https://github.com/johndoe" 
  ]
}
```

## Performance & Resources

- **Memory Requirements**:
  - Minimum: 512 MB RAM
  - Recommended: 1 GB RAM for multiple usernames
- **Processing Time**:
  - Single username: ~1-2 minutes
  - Multiple usernames: 2-5 minutes
  - Varies based on number of sites checked and response times


For more help, check the [Sherlock Project documentation](https://github.com/sherlock-project/sherlock) or raise an issue in the Actor's repository.
