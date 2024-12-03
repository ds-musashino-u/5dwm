import { Endpoints } from "./endpoints.mjs";

/**
 * /api/v1/upload
 * @module upload
 * @param {!string} token - Instance of Auth0
 * @param {!object} blob - BLOB
 * @param {?string} filename - Filename
 * @return {!object} - Result item
 */
export async function upload(token, blob, filename = null) {
    const formData = new FormData();

    if (filename === null) {
        formData.append("file", blob);
    } else {
        formData.append("file", blob, filename);
    }

    const response = await fetch(
        Endpoints.UPLOAD_URL,
        {
            mode: "cors",
            method: "POST",
            headers: {
                "X-Authorization": `Bearer ${token}`
            },
            body: formData,
        }
    );

    if (response.ok) {
        return await response.json();
    } else {
        throw new Error(response.statusText);
    }
}