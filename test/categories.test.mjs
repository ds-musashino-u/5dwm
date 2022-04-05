import assert from "assert";
import sinon from "sinon";
import { Category, getCategories, getCategory, addCategory, removeCategory } from "../src/presenters/categories.mjs"

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
    it("getCategories", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve([{ id: "1", name: "foobar", updated_at: "1970-01-01T09:00:00Z" }]) }));

        assert.equal(true, Array.isArray(await getCategories()));
    });
    it("getCategory", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve({ id: "1", name: "foobar", updated_at: "1970-01-01T09:00:00Z" }) }));

        assert.equal(true, await getCategory(1) instanceof Category);
    });
    it("addCategory", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve({ id: "1", name: "foobar", updated_at: "1970-01-01T09:00:00Z" }) }));

        assert.equal(true, await addCategory("foobar") instanceof Category);
    });
    it("removeCategory", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve({ id: "1", name: "foobar", updated_at: "1970-01-01T09:00:00Z" }) }));

        assert.equal(true, await removeCategory(1) instanceof Category);
    });
});