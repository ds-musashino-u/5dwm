import assert from "assert";
import sinon from "sinon";
import { Media, getMedia, getMedium } from "../src/presenters/media.mjs"

global.fetch = () => { };
global.window = {
    btoa: value => value
};

describe("media", function () {
    let fetchStub;

    beforeEach(() => {
        fetchStub = sinon.stub(global, 'fetch');
    });
    afterEach(() => {
        fetchStub.restore();
    });
    it("getMedia", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve([{ id: 1, url: "https://5dworldmap.com/foobar.png", type: "image/png", categories: ["foo", "bar"], address: "foo", description: "foo bar baz", username: "foobar", location: { type: "Point", coordinates: [105.85271637244875, 21.028344772352863] }, created_at: "1970-01-01T09:00:00Z" }]) }));

        assert.equal(true, Array.isArray(await getMedia("image/png")));
    });
    it("getMedium", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve({ id: 1, url: "https://5dworldmap.com/foobar.png", type: "image/png", categories: ["foo", "bar"], address: "foo", description: "foo bar baz", username: "foobar", location: { type: "Point", coordinates: [105.85271637244875, 21.028344772352863] }, created_at: "1970-01-01T09:00:00Z" }) }));

        assert.equal(true, await getMedium(1) instanceof Media);
    });
});