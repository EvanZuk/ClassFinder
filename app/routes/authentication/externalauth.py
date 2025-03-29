"""
This handles external authentication.
"""
from urllib.parse import urlparse
from flask import request, render_template
from app import app
from app.utilities.users import verify_user, create_token, readable_scopes
from app.utilities.responses import error_response, success_response

@app.route('/auth')
@verify_user
def external_auth():
    """
    This is the main entry point for external authentication.
    It verifies the user and redirects them to the appropriate page.
    """
    scopes = request.args.get('scopes')
    if scopes:
        scopes = scopes.strip().split(',')
    else:
        scopes = []
    # Remove duplicate scopes
    scopes = list(set(scopes))
    scopes_readable = []
    for scope in scopes:
        if scope in readable_scopes:
            scopes_readable.append(readable_scopes[scope])
        else:
            scopes_readable.append(scope)

    redirect_url = request.args.get('redirect_url')

    # Extract domain from redirect_url
    redirect_domain = None
    if redirect_url:
        parsed_url = urlparse(redirect_url)
        redirect_domain = parsed_url.netloc
        if not redirect_domain:
            return error_response("Invalid redirect URL", {"redirect_url": redirect_url})
    else:
        return error_response(
            "No redirect URL provided. Provide a redirect_url parameter, along with scopes seperated by commas.", 
            {
                "valid_scopes": readable_scopes
                
            }
        )
    return render_template(
        "external_auth.html",
        scopes_readable=scopes_readable,
        redirect_domain=redirect_domain,
        user=request.user
    )

@app.route('/auth', methods=['POST'])
@verify_user
def external_auth_post():
    """
    This handles the POST request for external authentication.
    It verifies the user and redirects them to the appropriate page.
    """
    scopes = request.args.get('scopes', '')
    if scopes:
        scopes = scopes.strip().split(',')
    else:
        scopes = []

    # Remove duplicate scopes
    scopes = list(set(scopes))

    redirect_url = request.args.get('redirect_url')

    # Redirect to the redirect_url with the token
    if redirect_url:
        # Check if redirect_url is a valid URL
        parsed_url = urlparse(redirect_url)
        if parsed_url.scheme and parsed_url.netloc:
            token = create_token(request.user.username, 'ext', None, scopes)
            #return redirect(f"{redirect_url}?token={token.token}")
            return success_response(
                "Redirecting to external application",
                {
                    "redirect_to": f"{redirect_url}?token={token.token}",
                }
            )
        return error_response("Invalid redirect URL", {"redirect_url": redirect_url})
    return error_response("No redirect URL provided")
