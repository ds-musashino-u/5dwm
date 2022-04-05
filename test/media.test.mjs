import assert from "assert";
import sinon from "sinon";
import { Location } from "../src/presenters/location.mjs";
import { Media, getMedia, getMedium, insertMedium, deleteMedium } from "../src/presenters/media.mjs"

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
    it("insertMedium", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve({ id: 1, url: "https://5dworldmap.com/foobar.png", type: "image/png", categories: ["foo", "bar"], address: "foo", description: "foo bar baz", username: "foobar", location: { type: "Point", coordinates: [105.85271637244875, 21.028344772352863] }, created_at: "1970-01-01T09:00:00Z" }) }));

        assert.equal(true, await insertMedium("https://5dworldmap.com/foobar.png", "image/png", ["foo", "bar"], "foo bar baz", "foobar", new Location(105.85271637244875, 21.028344772352863, "foo")) instanceof Media);
    });
    it("deleteMedium", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve({ id: 1, url: "https://5dworldmap.com/foobar.png", type: "image/png", categories: ["foo", "bar"], address: "foo", description: "foo bar baz", username: "foobar", location: { type: "Point", coordinates: [105.85271637244875, 21.028344772352863] }, created_at: "1970-01-01T09:00:00Z" }) }));

        assert.equal(true, await deleteMedium(1) instanceof Media);
    });
});