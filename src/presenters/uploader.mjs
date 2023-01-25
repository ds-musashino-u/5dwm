import { Endpoints } from "./endpoints.mjs";

/**
 * /api/v1/upload
 * @module upload
 * @param {!string} token - Instance of Auth0
 * @param {!string} dataURL - Data URL
 * @return {!object} - Result item
 */
export async function upload(token, dataURL) {
    const response = await fetch(
        Endpoints.UPLOAD_URL,
        {
            mode: "cors",
            method: "POST",
            headers: {
                "X-Authorization": `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ data: dataURL }),
        }
    );

    if (response.ok) {
        return await response.json();
    } else {
        throw new Error(response.statusText);
    }
}