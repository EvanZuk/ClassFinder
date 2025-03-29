# ClassFinder
ClassFinder was my solution to STEM's bad bell schedule, it tells you what classes you have, and allows external services to authenticate with it. Feel free to contribute.
## Authenticating to an external service
If you want to authenticate your service using ClassFinder credentials, you may create a redirect to `/auth`. Going to `/auth` without any parameters will give you a list of valid scopes you may use.
An example `/auth` request looks like: `/auth?redirect_url=http://localhost:5200/callback&scopes=read-email,read-misc`
Sending `/auth` with only a redirect_url is valid, and only gives your app access to a user's username, and role.
Once a user has clicked authenticate, they are redirected to `<redirect_url>?token=<token>`, where redirect_url is your redirect, and token is the resulting token. You may then get user data by sending API requests using the Authorization HTTP header with a bearer token, like `Authorization: Bearer <token>`. The most common request you can make is to `/api/v2/data`, where you can get data about the user you just authenticated with, along with any other data you requested.