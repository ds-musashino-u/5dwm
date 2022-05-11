import assert from "assert";
import sinon from "sinon";
import { search } from "../src/presenters/search.mjs"

global.fetch = () => { };
global.window = {
    btoa: value => value
};

describe("search", function () {
    let fetchStub;

    beforeEach(() => {
        fetchStub = sinon.stub(global, 'fetch');
    });
    afterEach(() => {
        fetchStub.restore();
    });
    it("search", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve({ count: 1, items: [{ id: 1, url: "https://5dworldmap.com/foobar.png", type: "image/png", categories: ["foo", "bar"], address: "foo", description: "foo bar baz", username: "foobar", location: { type: "Point", coordinates: [105.85271637244875, 21.028344772352863] }, created_at: "1970-01-01T09:00:00Z" }] }) }));

        const [items, count] = await search("dummy_token", ["foo"], ["bar"], ["baz"]);

        assert.equal(true, Array.isArray(items));
        assert.equal(true, typeof (count) === "number");
    });
});