import assert from "assert";
import sinon from "sinon";
import { getUsers } from "../src/presenters/users.mjs"

global.fetch = () => { };
global.window = {
    btoa: value => value
};

describe("users", function () {
    let fetchStub;

    beforeEach(() => {
        fetchStub = sinon.stub(global, 'fetch');
    });
    afterEach(() => {
        fetchStub.restore();
    });
    it("getUsers", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve([{ username: "foobar", email: "foobar@example.com", updated_at: "1970-01-01T09:00:00Z" }]) }));

        assert.equal(true, Array.isArray(await getUsers()));
    });
});