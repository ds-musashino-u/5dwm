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
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve({ count: 1, timestamp: 12345, took: 0.1, items: [{ id: 1, url: "https://5dworldmap.com/foobar.png", type: "image/png", categories: ["foo", "bar"], address: "foo", description: "foo bar baz", username: "foobar", location: { type: "Point", coordinates: [105.85271637244875, 21.028344772352863] }, created_at: "1970-01-01T09:00:00Z" }] }) }));

        const [items, count, timestamp] = await search("dummy_token", ["foo"], ["bar"], ["baz"], ["user"], "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==");

        assert.equal(true, Array.isArray(items));
        assert.equal(true, typeof (count) === "number");
        assert.equal(true, typeof (timestamp) === "number");
    });
});