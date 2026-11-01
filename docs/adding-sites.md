# Configuring status-code detection

Site definitions live in `sherlock_project/resources/data.json` and are validated
against `sherlock_project/resources/data.schema.json`. For the general contribution
process and target requirements, see the [adding sites guide](https://sherlockproject.xyz/adding-sites).

## Required and optional fields

Every target requires `url`, `urlMain`, `errorType`, and `username_claimed`.
`username_claimed` must identify an existing public profile so the target can be
checked for false negatives. Use `{}` as the username placeholder in `url`.

For `"errorType": "status_code"`, `errorCode` and `request_method` are optional:

| Field | Default behavior | When to set it |
| --- | --- | --- |
| `request_method` | `HEAD` for the string `"status_code"`; `GET` for other error types, including arrays such as `["status_code"]`. | Set `"GET"` when a site responds differently to HEAD, or specify another supported method required by its probe. Supported methods are `GET`, `HEAD`, `POST`, and `PUT`. |
| `errorCode` | Responses outside the 200–299 range indicate that the profile is absent. | Set an integer or list of integers to mark particular statuses (including 2xx) as absent. This supplements the default check; it does not make other non-2xx responses count as found. |

For example, this illustrative entry explicitly selects GET and identifies 404
as an absent profile:

```json
{
  "Example": {
    "url": "https://example.com/users/{}",
    "urlMain": "https://example.com/",
    "errorType": "status_code",
    "errorCode": 404,
    "request_method": "GET",
    "username_claimed": "existing-user"
  }
}
```

Listing 404 explicitly is optional and redundant with the default non-2xx check;
it is included here to show the field syntax. A custom 2xx code is appropriate
only when the site reliably uses that specific status for absent profiles.

This is a configuration example, not a target to add verbatim. Replace the URLs
and claimed username with verified values. Custom `headers` can be supplied when
the probe needs them; headers do not themselves select the request method.

## Check the actual response

Compare both an existing and a nonexistent username, using the same request
method and headers Sherlock will use. Do not infer existence from the browser's
rendered page alone. A site that returns HTTP 200 for both cases needs another
reliable signal, such as a missing-profile message; adding `errorCode: 404` cannot
correct that behavior. Authentication pages, rate limits, redirects, and
anti-bot responses can also make status-only checks unreliable.

Use `--site SITE_NAME --local --dump-response` with each test username to inspect
the configured local target. If `urlProbe` is set, inspect that endpoint too:
Sherlock queries it instead of the public profile URL. Verify both false-positive
and false-negative cases before submitting a target change.
