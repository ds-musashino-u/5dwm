import assert from "assert";
import sinon from "sinon";
import { getTypes } from "../src/presenters/types.mjs"

global.fetch = () => { };
global.window = {
    btoa: value => value
};

describe("types", function () {
    let fetchStub;

    beforeEach(() => {
        fetchStub = sinon.stub(global, 'fetch');
    });
    afterEach(() => {
        fetchStub.restore();
    });
    it("getTypes", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve(["image/png", "image/jpeg", "video/mp4"]) }));

        assert.equal(true, Array.isArray(await getTypes()));
    });
});