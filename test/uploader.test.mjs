import assert from "assert";
import sinon from "sinon";
import { upload } from "../src/presenters/uploader.mjs";

global.fetch = () => { };
global.window = {
    btoa: value => value
};

describe("uploader", function () {
    let fetchStub;

    beforeEach(() => {
        fetchStub = sinon.stub(global, 'fetch');
    });
    afterEach(() => {
        fetchStub.restore();
    });
    it("upload", async function () {
        fetchStub.returns(Promise.resolve({ ok: true, json: () => Promise.resolve({ id: "1", url: "https://static.5dworldmap.com/media/foo.png", type: "image/png", thumbnail_url: "https://static.5dworldmap.com/media/thumbnails/foo.png", created_at: "1970-01-01T09:00:00Z" }) }));

        const result = await upload("dummy_token", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==");

        assert.equal(true, result !== null && typeof result === "object");
        assert.equal(true, result["url"].startsWith("https://"));

        if ("thumbnail_url" in result) {
            assert.equal(true, result["thumbnail_url"].startsWith("https://"));
        }
    });
});