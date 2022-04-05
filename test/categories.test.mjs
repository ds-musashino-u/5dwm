import assert from "assert";
import sinon from "sinon";
import { Category, getCategories, getCategory, insertCategory, updateCategory, deleteCategory } from "../src/presenters/categories.mjs"

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
    it("insertCategory", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve({ id: "1", name: "foobar", updated_at: "1970-01-01T09:00:00Z" }) }));

        assert.equal(true, await insertCategory("foobar") instanceof Category);
    });
    it("updateCategory", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve({ id: "1", name: "foobar", updated_at: "1970-01-01T09:00:00Z" }) }));

        assert.equal(true, await updateCategory(1, "foobar") instanceof Category);
    });
    it("deleteCategory", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve({ id: "1", name: "foobar", updated_at: "1970-01-01T09:00:00Z" }) }));

        assert.equal(true, await deleteCategory(1) instanceof Category);
    });
});