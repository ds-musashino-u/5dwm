import { Endpoints } from "./endpoints.mjs";

/**
 * /api/v1/upload
 * @module upload
 * @param {!string} token - Instance of Auth0
 * @param {!object} blob - BLOB
 * @return {!object} - Result item
 */
export async function upload(token, blob) {
    const formData = new FormData();

    formData.append("file", blob);

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