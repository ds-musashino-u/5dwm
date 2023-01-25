import { Auth0Config } from "./auth0-config.mjs";

/**
 * Get access token
 * @module getAccessToken
 * @param {!object} auth0 - An instance of Auth0Client
 * @param {?string} audience - Audience
 * @return {!string} - Access token
 */
export async function getAccessToken(auth0, audience = null) {
    const accessToken = await auth0.getTokenSilently({
        authorizationParams: {
            audience: audience === null ? Auth0Config.AUDIENCE : audience
        }
    });

    if (accessToken.split(".").every(x => x.length > 0)) {
        return accessToken;
    }

    const idToken = await auth0.getIdTokenClaims();

    return idToken.__raw;
}
