import assert from "assert";
import sinon from "sinon";
import { Auth0Config } from "../src/presenters/auth0-config.mjs";
import { getAccessToken } from "../src/presenters/auth.mjs";

class Auth0Client {
    getTokenSilently(params) {
    }

    getIdTokenClaims() {
    }
}

describe("auth", function () {
    it("getAccessToken", async function () {
        const auth0 = new Auth0Client();
        let silentlyStub = sinon.stub(auth0, "getTokenSilently");
        const claimsStub = sinon.stub(auth0, "getIdTokenClaims");

        silentlyStub.withArgs({
            authorizationParams: {
                audience: Auth0Config.AUDIENCE
            }
        }).returns("foo.bar.baz");
        claimsStub.returns({__raw: "qux.quux.corge" });

        assert.equal(true, await getAccessToken(auth0, Auth0Config.AUDIENCE) === "foo.bar.baz");
        
        silentlyStub.restore();
        silentlyStub = sinon.stub(auth0, "getTokenSilently");
        silentlyStub.withArgs({
            authorizationParams: {
                audience: Auth0Config.AUDIENCE
            }
        }).returns("foo..bar");
        
        assert.equal(true, await getAccessToken(auth0, Auth0Config.AUDIENCE) === "qux.quux.corge");

        silentlyStub.restore();
        claimsStub.restore();
    });
});